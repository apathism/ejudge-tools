#!/bin/bash

for i in 0{1..9} {10..71}; do
    wkhtmltopdf $i.html $i.pdf
done
