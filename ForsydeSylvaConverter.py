#!/usr/bin/env python3

from math import e
import sys
import xml.etree.ElementTree as et
from jinja2 import Template
import os
import stat
import json

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
            trait = ""
            for trait in node.findall("./traits"):
                if (
                    trait.text == "moc::sdf::SDFComb"
                    or trait.text == "moc::sdf::SDFChannel"
                ):
                    trait = trait.text
                    flag_is_process_node = True
                    break

            if not flag_is_process_node:
                continue

            n = {}
            n["name"] = node.attrib["identifier"]
            n["type"] = trait
            
            if(n["type"] ==  "moc::sdf::SDFComb"):
                trait = ""
                for trait in node.findall("./traits"):
                    if trait.text.startswith("func"):
                        trait = trait.text
                        break
                n["func"] = trait

                if not n["func"]:
                    print ("ERROR: Undefined function implementation!")
                    exit(-1)

                prop_map = {}
                prop_name = []
                prop_value = []
                for pn in node.findall("./propertiesNames"):
                    prop_name.append(pn.text)
                for pv in node.findall("./propertiesValues"):
                    prop_value_map = {}
                    
                    values = []
                    indices = []
                    type_names = []
                    type_sizes = []
                    for v in pv.findall("./values"):
                        values.append(v.attrib["intValue"])
                    for i in pv.findall("./indexes"):
                        indices.append(i.text)
                    for i in pv.findall("./typeName"):
                        type_names.append(i.text)
                    for i in pv.findall("./typeSize"):
                        type_sizes.append(i.attrib["intValue"])

                    # Check the the vectors has the same size, that means all the ports has all the needed fields
                    if(len(values) != len(indices) or len(values) != len(type_names) or len(values)!=len(type_sizes)):
                        print("Error: Some port don't have sufficient properties!")
                        exit(-1)

                    for i in range(len(indices)):
                        prop_value_map[indices[i]] = {"value":values[i], "index":indices[i], "type_name": type_names[i], "type_size": type_sizes[i]}
                    prop_value.append(prop_value_map)
                for i in range(len(prop_name)):
                    prop_map[prop_name[i]] = prop_value[i]
                n["prop"] = prop_map
                    

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
                            n["ports"][e["src_port"]]["io"] = "out"
                        elif n["ports"][e["src_port"]]["io"] == "in":
                            n["ports"][e["src_port"]]["io"] = "in_out"
                        elif n["ports"][e["src_port"]]["io"] == "out":
                            pass
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
                            n["ports"][e["dst_port"]]["io"] = "in"
                        elif n["ports"][e["dst_port"]]["io"] == "in":
                           pass
                        elif n["ports"][e["dst_port"]]["io"] == "out":
                             n["ports"][e["dst_port"]]["io"] = "in_out"
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
        original_stdout = sys.stdout
        with open(filename, "w+") as f:
            f.write(json.dumps(sylva_sdf, indent=4, sort_keys=True))
    
    def save_dot(self, filename, sylva_sdf):
        data = {"actors":[{"index": n["index"], "name": n["name"]} for n in sylva_sdf["actors"]], "edges":[e for e in sylva_sdf["edges"]]}
        for e in data["edges"]:
            for n in sylva_sdf["actors"]:
                if n["index"] == e["src_actor"]:
                    e["src_count"] = n["output_ports"][e["src_port"]]["count"]
                if n["index"] == e["dest_actor"]:
                    e["dest_count"] = n["input_ports"][e["dest_port"]]["count"]

        tm = Template("""
digraph g{
    
    {% for n in sdf.actors -%}
    {{n.index}} [shape=box, label="{{n.name}}\\n({{n.index}})"];
    {% endfor -%}

    {% for e in sdf.edges -%}
    {{e.src_actor}} -> {{e.dest_actor}} [headlabel="{{e.src_count}}", taillabel="{{e.dest_count}}"];
    {% endfor -%}
}        
""")
        msg = tm.render(sdf=data)
        with open(filename, "w+") as f:
            f.write(msg)

    def save_sh(self, filename):
        tm = Template("""
#!/usr/bin/env bash

for file in ./*.dot; do
basename=${file%.*}
dot -Tpdf ${basename}.dot -o ${basename}.pdf
done       
""")
        msg = tm.render()
        with open(filename, "w+") as f:
            f.write(msg)

        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)


class ForsydeSylvaConverter:
    """SDF converter from Forsyde to Sylva"""

    def __init__(self):
        pass

    def convert(self, forsyde_sdf):

        # Remove the SDFChannel nodes and reconnect the edges
        add_edges = []
        for node in forsyde_sdf["nodes"]:
            if node["type"] == "moc::sdf::SDFChannel":
                for e0 in forsyde_sdf["edges"]:
                    if e0["src"] == node["name"] and e0["src_port"] == "consumer":
                        for e1 in forsyde_sdf["edges"]:
                            if e1["dst"] == node["name"] and e1["dst_port"] == "producer":
                                e = {"src": e1["src"], "src_port": e1["src_port"], "dst": e0["dst"], "dst_port": e0["dst_port"]}
                                add_edges.append(e)

        for e in add_edges:
            forsyde_sdf["edges"].append(e)

        for node in forsyde_sdf["nodes"]:
            if node["type"] == "moc::sdf::SDFChannel":
                flag_changed=True
                while(flag_changed):
                    flag_changed = False
                    for e0 in forsyde_sdf["edges"]:
                        if e0["src"] == node["name"]:
                            forsyde_sdf["edges"].remove(e0)
                            flag_changed = True
                            break
                    for e0 in forsyde_sdf["edges"]:
                        if e0["dst"] == node["name"]:
                            forsyde_sdf["edges"].remove(e0)
                            flag_changed = True
                            break

        sylva_sdf = {"actors":[], "edges":[]}

        for e in forsyde_sdf["edges"]:
            sylva_sdf ["edges"].append({"src_actor": e["src"], "src_port": e["src_port"], "dest_actor": e["dst"], "dest_port": e["dst_port"]})

        name_to_id = {}
        id_to_name = {}
        i=0
        for node in forsyde_sdf["nodes"]:
            if node["type"] == "moc::sdf::SDFComb":
                name_to_id[node["name"]] = i
                id_to_name[i] = node["name"]
                n = {}
                n["index"] = i
                n["name"] = node["func"]
                sylva_sdf["actors"].append(n)
                i=i+1

                j=0
                k=0
                output_ports = []
                input_ports = []
                name_to_port ={}
                for port_name, port in node["ports"].items():
                    p = {}
                    p["name"] = port["name"]
                    if port["io"] != "in" and port["io"] != "out":
                        continue
                    if port["io"] == "in":
                        p["index"] = j
                        p["count"] = int(node["prop"]["consumption"][p["name"]]["value"])
                        p["type"] = {"name":node["prop"]["consumption"][p["name"]]["type_name"], "size":int(node["prop"]["consumption"][p["name"]]["type_size"])}
                        input_ports.append(p)
                        name_to_port[p["name"]] = j
                        j=j+1
                    elif port["io"] == "out":
                        p["index"] = k
                        p["count"] = int(node["prop"]["production"][p["name"]]["value"])
                        p["type"] = {"name":node["prop"]["production"][p["name"]]["type_name"], "size":int(node["prop"]["production"][p["name"]]["type_size"])}
                        output_ports.append(p)
                        name_to_port[p["name"]] = k
                        k=k+1
                n["input_ports"] = input_ports
                n["output_ports"] = output_ports
                
                for e in sylva_sdf["edges"]:
                    if e["src_actor"] == node["name"]:
                        e["src_actor"] = n["index"]
                        e["src_port"] = name_to_port[e["src_port"]]
                        
                    if e["dest_actor"] == node["name"]:
                        e["dest_actor"] = n["index"]
                        e["dest_port"] = name_to_port[e["dest_port"]]

        for node in sylva_sdf["actors"]:
            node ["prev"] = []
            node ["next"] = []
            for e in sylva_sdf["edges"]:
                if e["src_actor"] == node["index"]:
                    node["next"].append(e)
                if e["dest_actor"] == node["index"]:
                    node["prev"].append(e)

        return sylva_sdf



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Wrong argument!")
        print("Use: ./ForsydeSylvaConverter.py <input xml> <output directory>")
        exit(-1)

    forsyde_xml = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    sylva_dot = output_path + "/output.dot"
    sylva_sdfg = output_path + "/output.sdfg"
    convert_sh = output_path + "/convert.sh"

    io = FileIO()
    forsyde_sdf = io.load(forsyde_xml)
    conv = ForsydeSylvaConverter()
    sylva_sdf = conv.convert(forsyde_sdf)
    io.save_dot(sylva_dot, sylva_sdf)
    io.save(sylva_sdfg, sylva_sdf)
    io.save_sh(convert_sh)
