#!/usr/bin/env bash

NEW_VERSION=${1?"usage $0 <new version>"}

echo "Updating versions to version ${NEW_VERSION}"
find . -name "Cargo.toml" -exec perl -p -i -e "s/^version = \".*\"$/version = \"$NEW_VERSION\"/g" {} \;


if [[ "${NEW_VERSION}" == "${NEW_VERSION/-SNAPSHOT/}" ]]
then
    perl -p -i -e \
        "s/^snips-nlu-parsers-ffi-macros = \{.*\}$/snips-nlu-parsers-ffi-macros = { git = \"https:\/\/github.com\/snipsco\/snips-nlu-parsers\", tag = \"$NEW_VERSION\" }/g" \
        python/ffi/Cargo.toml
else
    perl -p -i -e \
        "s/^snips-nlu-parsers-ffi-macros = \{.*\}$/snips-nlu-parsers-ffi-macros = { path = \"..\/..\/ffi\/ffi-macros\" }/g" \
        python/ffi/Cargo.toml
fi

echo "$NEW_VERSION" > python/snips_nlu_parsers/__version__
