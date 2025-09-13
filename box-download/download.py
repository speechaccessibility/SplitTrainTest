import os, argparse, datetime, requests, re
from box_sdk_gen import BoxClient, BoxDeveloperTokenAuth

def main(developer_token, folders, regex):
    auth: BoxDeveloperTokenAuth = BoxDeveloperTokenAuth(token=developer_token)
    client: BoxClient = BoxClient(auth=auth)
    root_folder = os.getcwd()

    while len(folders) > 0:
        folder_name = folders.pop(0)
        folder_id = folders.pop(0)
        os.makedirs(folder_name, exist_ok=True)
        os.chdir(folder_name)
        for item in client.folders.get_folder_items(folder_id).entries:
            if re.search(regex, item.name):
                print(item.id, item.name, datetime.datetime.now().isoformat())
                success=0
                while success==0:
                    try:
                        with open(item.name, 'wb') as output_stream:
                            client.downloads.download_file_to_output_stream(item.id, output_stream)
                            success=1
                    except requests.exceptions.ConnectionError:
                        print("Received requests.exceptions.ConnectionError; trying again")
        os.chdir(root_folder)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
        Attempt to download all files from a specified Box folder to the current local directory.
        
        USAGE: python download.py <developer_token> <dirname1> <dir_id1> [<dirname2> <dir_id2>...]

        Here's a sample from one of my runs:
        python download.py X8uuOKI6TrpjbELuvVsJkAn6uoYWtz5b Dev 338866207012 Test1 338865316557 Test2 338867286130 Train 338867617703
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-r','--regex',
        action='store',
        help="""
        Only download items whose filename matches the regex.
        """)
    parser.add_argument(
        'developer_token',
        action='store',
        help="""
        A developer token is a string provided by Box when you create a Custom App at
        https://app.box.com/developers/console, go to the "Configuration" tab, 
        use OAuth 2.0 authentication, make sure to select both
        'Read all files and folders stored in Box' and
        'Write all files and folders stored in Box,' then 
        select 'Generate Developer Token.'
        It is short-lived; make a new one each time you use this program.
        """)
    parser.add_argument(
        'folders',
        action='store',
        nargs='*',
        help="""
        List the directory names and folder IDs from which you wish to download files.

        Each folder_id is obtained from box.com, for example
        in https://uofi.app.box.com/folder/334095714757, the folder_id is 334095714757.

        Each directory name will be created if it does not exist, then this program will
        change to that directory, and download all non-subfolder content from the corresponding
        box folder_id, then change back to the current directory.
        """
    )
    args = parser.parse_args()
    if len(args.folders) % 2 != 0:
        raise RuntimeError("""
        `folders' must be an even-length list, containing <foldername> <folder_id> pairs.
        """)
    
    main(args.developer_token, args.folders, args.regex)
    
