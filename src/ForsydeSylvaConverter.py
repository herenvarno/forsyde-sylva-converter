import sys
import os
import xml.etree.ElementTree as et
import networkx as nx
import matplotlib.pyplot as plt
import math


class SDF:
    """SDF Data Structure"""

    def __init__(self):
        pass


class FileIO:
    """IO class for XML files"""

    def __init__(self):
        pass

    def load(self, filename):
        tree = et.parse(filename)
        root = tree.getroot()

        sdf = {"nodes": [], "edges": []}
        for node in root.findall("./nodes"):
            flag_is_process_node = False
            for trait in node.findall("./traits"):
                print(trait.text)
                if (
                    trait.text == "moc::sdf::SDFComb"
                    or trait.text == "moc::sdf::SDFChannel"
                ):
                    flag_is_process_node = True
                    break

            if not flag_is_process_node:
                continue

            n = {}
            n["name"] = node.attrib["identifier"]
            n["ports"] = {}
            for port in node.findall("./ports"):
                p = {}
                p["name"] = port.text
                p["io"] = ""
                n["ports"][p["name"]] = p
            sdf["nodes"].append(n)
        for edge in root.findall("./edges"):
            flag_is_data_edge = False
            for trait in edge.findall("./traits"):
                print(trait.text)
                if trait.text == "moc::sdf::SDFDataEdge":
                    flag_is_data_edge = True
                    break

            if not flag_is_data_edge:
                continue

            e = {}
            e["src"] = edge.attrib["source"]
            if "sourceport" in edge.attrib:
                e["src_port"] = edge.attrib["sourceport"]
                for n in sdf["nodes"]:
                    if n["name"] == e["src"]:

                        if e["src_port"] not in n["ports"]:
                            print(
                                "ERROR: Input port ", e["src_port"], " doesn't exist!"
                            )
                            exit(-1)
                        if n["ports"][e["src_port"]]["io"] == "":
                            n["ports"][e["src_port"]]["io"] = "in"
                        elif n["ports"][e["src_port"]]["io"] == "in":
                            pass
                        elif n["ports"][e["src_port"]]["io"] == "out":
                            n["ports"][e["src_port"]]["io"] = "in_out"
                        elif n["ports"][e["src_port"]]["io"] == "in_out":
                            pass
                        else:
                            print("ERROR: Port ", e["src_port"], " io type is wrong!")
                            exit(-1)
            else:
                e["src_port"] = ""
            e["dst"] = edge.attrib["target"]
            if "targetport" in edge.attrib:
                e["dst_port"] = edge.attrib["targetport"]
                for n in sdf["nodes"]:
                    if n["name"] == e["dst"]:
                        if e["dst_port"] not in n["ports"]:
                            print(
                                "ERROR: Output port ", e["dst_port"], " doesn't exist!"
                            )
                            exit(-1)
                        if n["ports"][e["dst_port"]]["io"] == "":
                            n["ports"][e["dst_port"]]["io"] = "out"
                        elif n["ports"][e["dst_port"]]["io"] == "in":
                            n["ports"][e["dst_port"]]["io"] = "in_out"
                        elif n["ports"][e["dst_port"]]["io"] == "out":
                            pass
                        elif n["ports"][e["dst_port"]]["io"] == "in_out":
                            pass
                        else:
                            print("ERROR: Port ", e["dst_port"], " io type is wrong!")
                            exit(-1)
            else:
                e["dst_port"] = ""
            sdf["edges"].append(e)
        return sdf

    def save(self, filename, sylva_sdf):
        pass


class Visulizer:
    """Visulize the basic SDF"""

    def __init__(self):
        pass

    def visualize(self, sdf):
        g = nx.MultiDiGraph()
        for n in sdf["nodes"]:
            g.add_node(n["name"])
        for e in sdf["edges"]:
            g.add_edge(e["src"], e["dst"])

        options = {
            "with_labels": True,
            "node_size": 3000,
            "node_shape": "s",
            "node_color": "#aaaaaa",
        }
        k = 5 / math.sqrt(g.order())
        subax1 = plt.subplot(111)
        nx.draw(g, pos=nx.spring_layout(g, k), **options)
        plt.show()


class ForsydeSylvaConverter:
    """SDF converter from Forsyde to Sylva"""

    def __init__(self):
        pass

    def convert(self, forsyde_sdf):
        pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong argument!")
        exit(-1)

    forsyde_xml = sys.argv[1]

    io = FileIO()
    sdf = io.load(forsyde_xml)
    print(sdf)

    vs = Visulizer()
    vs.visualize(sdf)
