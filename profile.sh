vamux() {
    if [[ "$1" =~ "-h" || "$1" =~ "--help" ]]; then
        echo "Usage: vamux [options]"
        echo "Options:"
        echo "  -h, --help       Show this help message"
        echo "  --nogui          Run without GUI"
        echo "  --video          Specify video file path"
        echo "  --audio          Specify audio file path"
        echo "  --output         Specify output file path"
        echo ""
        echo "If run with GUI, you can also drag and drop files onto the GUI for selection."
    else
        rez env pyside2 -c "/STUDIO/scripts/vamux $*"
    fi
}