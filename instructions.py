def show_instructions(log_function):
    instructions = (
        "Welcome to YTDL GUI!\n\n"
        "Steps to use:\n"
        "1. Enter the video URL in the 'Enter video URL' field.\n"
        "2. Press 'Get available qualities' to fetch video.\n"
        "3. Select the desired video quality from the dropdown.\n"
        "4. Choose the folder to save the video.\n"
        "5. Select the output format (mp4, mkv).\n"
        "6. Optionally, enter a custom filename.\n"
        "7. Press 'Download' to start the video download.\n\n"
        "Enjoy downloading your videos!"
    )
    log_function(instructions)
