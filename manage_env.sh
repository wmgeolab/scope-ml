#!/bin/bash

# Function to manage the Docker environment
manage_env() {
    local action=$1
    local interactive_mode=$2 # New parameter to determine if interactive mode is enabled

    echo "$action the environment..."

    local compose_file="docker-compose.yaml"
    local up_options="--force-recreate --build"

    # If interactive mode is not enabled, run in detached mode
    if [ "$interactive_mode" != "yes" ]; then
        up_options="$up_options -d"
    fi

    case "$action" in
        start)
            docker compose -f $compose_file up $up_options
            ;;
        stop)
            docker compose -f $compose_file down
            ;;
        rebuild)
            docker compose -f $compose_file down
            docker compose -f $compose_file build --no-cache
            docker compose -f $compose_file up $up_options
            ;;
        clean)
            # Remove all __pycache__ folders
            find . -type d -name "__pycache__" -exec rm -r {} +
            ;;
        *)
            echo "Invalid action: $action. Please use 'start', 'stop', or 'rebuild'."
            exit 1
            ;;
    esac
}

# Default values
interactive_mode="no"

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        start|stop|rebuild|clean)
            action="$1"
            ;;
        -i)
            interactive_mode="yes"
            ;;
        *)
            echo "Invalid argument: $1"
            echo "Usage: $0 <action> [-i]"
            echo "<action> can be 'start', 'stop', 'clean', or 'rebuild'."
            echo "Use -i for interactive mode (not detached)."
            exit 1
            ;;
    esac
    shift
done

# Validate action argument
if [[ -z "$action" ]]; then
    echo "Action not set. Please specify 'start', 'stop', or 'rebuild'."
    exit 1
fi

# Pass action and interactive mode flag to the manage_env function
manage_env $action $interactive_mode
