#!/bin/bash

tmp_file=/tmp/swagger.json.tmp

function output_doc() {
    target=$1
    python "troops/${1}.py" -S > $tmp_file
    bootprint openapi $tmp_file docs
    mv docs/index.html "docs/${target}.html"
}

output_doc recruiter
output_doc commander
output_doc leader

rm $tmp_file


