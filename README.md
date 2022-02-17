# Forsyde-Sylva-Converter

Forsyde-Sylva-Converter is an SDF converter from that bridges between Forsyde and Sylva.

It convert a subgraph that has been identified and isolated for synthesis to the format that Sylva (the SiLago application-level synthesis tool) recongnize.

Both Forsyde and Sylva can recongnize SDF graphs, but the detailed SDF description is different on both platform. Forsyde uses an xml-based SDF description file that contains not only the SDF graph but also the other information, such as the implementation platform. Sylva uses a json-based SDF description file that contains pretty much only the SDF with some add-on features (ports, data-types, function name, etc).

## Usage

To convert the SDF file, one should use the following command:

```
./ForsydeSylvaConverter <input xml file> <output directory>
```

The *input xml file* is the Forsyde SDF description file. The *output directory* is the directory that all the output files will be generated. The output directory must exist.

## Output Files

There are three files that will be generated: *output.sdfg*, *output.dot*, and *convert.sh*.

The *output.sdfg* is the SDF description file that will be used by Sylva.

The *output.dot* is the SDF visualization file that can be converted to a picture in PDF format.

The *converter.sh* is the script that convert the *output.dot* to PDF file.
