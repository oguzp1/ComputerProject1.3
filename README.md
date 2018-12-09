# ComputerProject1.3
RPC-based secure and fault tolerant distributed file system.
Created for Computer Project I course at Istanbul Technical University in Fall 2018.

## Requirements
Python 3.5 or above.
Install requirements in the repository.

## Getting Started
To run the program do the following:
1) Run the name server
 ```
python name_server.py
```
2) Run storage server
```
python rpc_server.py <server_id> <port>
```
3) Run client <br/>
    * To sign up:
        ```
        python rpc_client.py signup <username> <password>
        ```

    * To log in:
        ```  
        python rpc_client.py login <username> <password>
        ```

## How to Use
The user interacts only with the client. When logged in, the program allows the following options: <br/>
- Change directory: **changedir** `<directory-path>`
- Create directory: **makedir** `<directory-path>`
- Delete directory: **deletedir** `<directory-path>`
- Upload file: **upload** `<directory-path>` `<directory-path>`
- Delete file: **delete** `<directory-path>`
- Fetch file: **fetch** `<directory-path>` `<directory-path>`
- Exit: **exit**

These options can be used as command-line commands.


## About the Project
## Name Server
The name server keeps a database to store user, file and server data in separate tables. It also implements methods to alter these tables and serve data when requested, such as deleting and saving to databases, getting user credentials and server addresses. 
The tables are as shown below:

- Users table:
    | USERID   | USERNAME  |  PASSWORD  | SALT  | 
    |------|------|------|------|------|------|
    |integer|text|text|text|
- Files table:

    | FILEID   | USERID  |  SERVERID  |  PATH  | FILENAME | ISBACKUP |FILEHASH | LASTMODIFIED | USERID | SERVERID |
    |------|------|------|------|------|------|------|------|------|-------|
    |integer|integer|integer|integer|text|integer|text|integer|FK|FK|

- Server table:
    | SERVERID   | ADDRESS |
    |------|------|
    |integer|text|

It is implemented using SimpleXMLRPCServer class of [xmlrpc](https://docs.python.org/3.7/library/xmlrpc.html) module of Python. The methods implemented by name server can be called by both the client and the server through RPC, as it aims to ensure the communication between the two and them and itself.

## Server
The server stores files uploaded by the user. In order to guarantee redundancy, every server has a backup server that stores the same files. Servers have two types of directories, one named by the user who owns the directory (*'<user_id>'*) one named by the user and marked as backup (*'<user_id>_backup'*). When a file is uploaded, its hash is stored in the database. When the file is being fetched, it's hash is recalculated and compared to the hash recorded in the database. If it does not match, the copy in the backup server is checked and sent to the client.
The server implements methods to get owner and backup info, hash files, get filenames, create and delete directories and upload, delete and send files. Some of these functions are called by the client to perform the listed actions and others are used internally.


## Client 
The client implements the parts of the system the user directly interacts with.
It connects to name server using a proxy to connect to the server the user's files are hosted. It operates in two modes: sign up and log in. In sign-up mode, it makes a request to the name server to register the user. The name server checks whether the username is unique and registers the user if no problems occur. In login mode, the client presents the user with multiple options as explained in [How to Use](#How-to-Use). While uploading and downloading files, files are encyrpted and decrpyted on client-side. Only encrypted binaries of files are kept on servers.

## Security and Fault Tolerance
To ensure security, passwords are hashed using a user-specific salt and the files are encrypted using the hashed password. Users can navigate through their directories but cannot move up after they reach the directory named after their user IDs. 
When the user wants to update a file, the old version is replaced by the new one and its hash is recalculated. The most recent hash is kept in the database of name server and when the user wants to fetch the file, this hash is compared to the hash calculated at the time of request. When hashes don't match, the server connects to the backup server to check the hash of the backup file. Keeping backup files and keeping and comparing hashes ensures currency. [bcrypt](https://pypi.org/project/bcrypt/) and [cryptography](https://pypi.org/project/cryptography/) are used to hash passwords and file binaries respectively. 

## RPC
RPC is a form of inter-process communication that allows one program to make calls to execute a method on another machine. The fact that machines where the call was made and the method is executed are different is irrelevant to the programmer as the programmer makes calls as if they are being executed locally. The communication happens between client(s) and server(s). Since [xmlrpc](https://docs.python.org/3.7/library/xmlrpc.html) is used, client(s) and server(s) communicate through XML documents. The client uses a proxy to connect to a given server. 