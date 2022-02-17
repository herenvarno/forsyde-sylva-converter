
#!/usr/bin/env bash

for file in ./*.dot; do
basename=${file%.*}
dot -Tpdf ${basename}.dot -o ${basename}.pdf
done       