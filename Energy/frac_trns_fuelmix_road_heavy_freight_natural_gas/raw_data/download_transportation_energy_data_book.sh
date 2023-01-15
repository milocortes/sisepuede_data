#!/bin/bash

echo "Descarga de Transportation Energy Data Book 29-40"

wget https://fraser.stlouisfed.org/files/docs/publications/doe/tedb_edition{29..40}.pdf

mv *.pdf pdfs