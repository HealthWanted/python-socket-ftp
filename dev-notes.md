# Socket project
- Like HTTP header: Client should first send header to server. According to header server take corresponsd action
- Like [HTTP Status Code](https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html): Server should also return status code to client, client should analyze it
- User input always with `.strip()`
- Rather write "redundant code" than use "if-else" in loop to lower the performance (e.g: send file with check if use md5)

## FTP sys process
client & server

1. Check the system access: `verify_args` +  `parser = optparse.OptionParser()`

    Start with command, means when instantiate the client/server handler need verify the command args -- verify args need to be the access of then whole program: `__init__()` method in class (main.ArgvHandler()) can help

2. Access the system's initiate method and make connection
    - Server: `func = getattr(self, args[0], None)` + `socketserver.ThreadingTCPServer((settings.HOST, settings.PORT), FTPHandler)`
    - Client: `self.make_connection()` + `ftp.interactive()`
3. Loop recive/send data: use data_header to communicate and decide which method is required

## Socket file transmission

- Better not to use `sendall(file_obj.read())`: read whole file into memory then send.
- Buffer and bandwidth will limit the data size, not possible to sent an big file at once, even client ready to receive large data: `data = client.recv(1024000)`
- Socket send data with bytes: use 'wb'(file receiver) / 'rb' (file sender)
- Filename + Filesize is essential

Divide into "file" sender/receiver (!= client/server)

### File receiver
- (Neccessary if it's client)Tell sender the filename that will receive: `self.sock.send(json.dumps(data_header).encode('utf-8'))`
- Check the status code from sender if sender is server, 
- Get filesize
- **Send back one byte data in case of sticky package: `self.sock.send(b'0')`**
- Open a file with 'wb': `with open(base_filename, 'wb') as file_obj`
- Get the file size from sender then loop receive the till the reveived file size added to sender's file size

### File sender
- (Neccessary if it's server) Receive the file name, check whether the file is exist: `if os.path.isfile(file_abs_path)`
- If exist, send the filesize + OK status code back to client
- **Receive one byte data in case of sticky package: `self.request.recv(1)`**
- Open a file with 'rb' loop to send



## Issue of sticky package
Assume send 3 parts of data at one flow: data header + file data + file md5 value

These 3 parts of data will stick together: data header contain file data, file data contain md5

### Solution 1
Separate them by:
- Sender: receive one byte of data in the middle of send (data header + file data ) & (file data + file md5 value) -- `self.request.recv(1)` **send different part of data need recv() in between**
- Receiver: send one byte of data in the middle of recv (data header + file data ) & (file data + file md5 value) -- `self.sock.send(b'9')` **receive  different part of data need send() in between**