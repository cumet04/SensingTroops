#!/bin/bash

tmpdir_base="/tmp/_swagger_tmp/"

function output_doc() {
    target=$1
    tmpdir=$tmpdir_base$target
    mkdir -p $tmpdir
    python "troops/${1}.py" -S > $tmpdir/tmp.json
    bootprint openapi $tmpdir/tmp.json $tmpdir
    mv ${tmpdir}"/index.html" docs/$target".html"
}

output_doc recruiter &
output_doc commander &
output_doc leader &
wait
rm -rf $tmpdir_base
