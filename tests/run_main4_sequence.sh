#!/usr/bin/env bash
set -e

# Resolve directory of this script so the runner works from any CWD
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Runner sequence: add friend → create trip → accept trip → add expense
echo "Run add friend"
# Prefer running with the tests venv, then backend venv, then system python
tests_venv="$script_dir/.venv/bin/python"
backend_venv="$script_dir/../backend/.venv/bin/python"
if [ -x "$tests_venv" ]; then
	PYTHON_EXEC="$tests_venv"
elif [ -x "$backend_venv" ]; then
	PYTHON_EXEC="$backend_venv"
else
	PYTHON_EXEC="python3"
fi

# helper: wait for result file to contain DONE
wait_for_done() {
	local file="$1"
	local timeout=${2:-120}
	local elapsed=0
	local interval=1
	while [ $elapsed -lt $timeout ]; do
		if [ -f "$file" ]; then
			if grep -q "^DONE" "$file" >/dev/null 2>&1; then
				echo "Found DONE in: $file"
				return 0
			fi
		fi
		sleep $interval
		elapsed=$((elapsed + interval))
	done
	echo "Timeout waiting for DONE in $file" >&2
	return 1
}

"$PYTHON_EXEC" "$script_dir/main4_add_friend.py"
wait_for_done "$script_dir/main4_add_friend_results.txt" 180

echo "Run accept friend"
"$PYTHON_EXEC" "$script_dir/main4_accept_friend.py"
wait_for_done "$script_dir/main4_accept_friend_results.txt" 180

echo "Run create trip"
"$PYTHON_EXEC" "$script_dir/main4_create_trip.py"
wait_for_done "$script_dir/main4_create_trip_results.txt" 180

echo "Run accept trip"
"$PYTHON_EXEC" "$script_dir/main4_accept_trip.py"
wait_for_done "$script_dir/main4_accept_trip_results.txt" 180

echo "Run add expense"
"$PYTHON_EXEC" "$script_dir/main4_add_expense.py"
wait_for_done "$script_dir/main4_add_expense_results.txt" 240

echo "Done"
