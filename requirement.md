# Function req
1. Multiple user can login at the same time
2. User has home dir, user can only visit their own home dir
3. User has their own disk space size
4. User can oprate dir like `cd`, `ls`
5. Upload + download file and check the consistency of file
6. Show process of file transmission
7. Resume break point

# Analyze req
- *Multiple user can login at the same time*: "socket server" + "ThreadingTCPServer"
- *User has home dir, user can only visit their own home dir*: 
- *User has their own disk space size*: user data is dict
- *User can oprate dir like `cd`, `ls`*
- *Upload + download file and check the consistency of file*: md5
- *Show process of file transmission*: Total file size / current received file size
- *Resume break point*: server start at the point of last time file transmission break -- prerequisite: client save the data including break point and send to server, server use `seek()`