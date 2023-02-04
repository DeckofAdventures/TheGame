
# NOTE: `/` characters may need to change to `\` on Windows

$Root = "/Users/cb/Documents/temp/creative/TheGame"
$Yaml_paths = $Root + "/docs/src/1_Mechanics/*yaml"
$yamls = Get-ChildItem -Path $Yaml_paths

foreach ($yaml in $yamls) {
    cp $yaml $Root"/automation/_input/"
}
