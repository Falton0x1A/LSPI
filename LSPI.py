import subprocess
import re
from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True
# Define the allowed commands and their corresponding parameter patterns
allowed_commands = {
    'chmod': r'^chmod(\s+-\w+)*$',
    'sudo': r'^sudo(\s+-\w+)*$',
    'visudo': r'^visudo$',
    'chroot': r'^chroot(\s+-\w+)*$',
    'last': r'^last(\s+-\w+)*$',
    'file': r'^file(\s+-\w+)*$',
    'ip': r'^ip(\s+-\w+)*$',
    'kill': r'^kill(\s+-\w+)*$',
    'setfacl': r'^setfacl(\s+-\w+)*$',
    'getfacl': r'^getfacl(\s+-\w+)*$',
    'ss': r'^ss(\s+-\w+)*$',
    'lsof': r'^lsof(\s+-\w+)*$',
}
#-------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')
#-------------------------------------------------------------------------------------------------------------------
@app.route('/interpret', methods=['POST'])
def interpret():
    command = request.form['command']
    print(f"Command received: {command}") # Debugging reasons

    # Validate the command against the allowed_commands patterns
    if command not in allowed_commands or not re.match(allowed_commands[command], command):
        error_message = f"Invalid command or parameters: {command}"
        return render_template('index.html', error_message=error_message)

    # Execute the command and capture the output
    try:
        output = subprocess.check_output(['man', command], stderr=subprocess.STDOUT)
        output = output.decode('utf-8')  # Convert bytes to string
    except subprocess.CalledProcessError as e:
        # Handle errors when the command is not found in the man pages
        error_output = e.output.decode('utf-8')
        if 'No manual entry' in error_output:
            error_message = f"No manual entry for '{command}'"
            return render_template('index.html', error_message=error_message)
        else:
            error_message = "An error occurred while executing the command"
            return render_template('index.html', error_message=error_message)

    # Extract relevant information from the man page using regular expressions
    sections = re.split(r'\n([A-Z]+)\n', output)[1:]  # Split into sections based on headings
    headings = sections[::2]  # Extract the headings
    content = sections[1::2]  # Extract the content

    # Combine headings and content into a dictionary for easier display
    man_page = {heading: content[i] for i, heading in enumerate(headings)}

    return render_template('index.html', command=command, man_page=man_page)
#-------------------------------------------------------------------------------------------------------------------
@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.form['command']
    parameter = request.form['parameter']
    print(f"Command received: {command} {parameter}")  # Debugging purposes

    try:
        command_with_parameter = f"man {command} | grep .{parameter},"
        # Making the command to execute
        output = subprocess.check_output(command_with_parameter, shell=True).decode('utf-8')
        # shell = true required for pipe (|) command

        return render_template('index.html', command=command_with_parameter, man_grep_output=output, man_page=None)
        # Man_page = none required to not display the man page before the new output
    except subprocess.CalledProcessError as e:
        # Handle errors when the command is not found
        error_output = e.output.decode('utf-8')
        if 'No manual entry' in error_output:
            error_message = f"No manual entry for '{command}'"
            return render_template('index.html', error_message=error_message)
        else:
            error_message = "An error occurred while executing the command"
            return render_template('index.html', error_message=error_message)
        
    # Handle other error cases if needed
    return render_template('index.html', command=command, man_grep_output=None, man_page=None)
#-------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run()
