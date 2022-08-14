# mmL
mmL is a python library with many different purposes, such as encryption (symetric and asymetric), random number generation (including primes) and multiplayer connection.

***This project is not completed. Bugs may be very common.***

## License
This project  is in the public domain. See LICENSE for more information.

## Multiplayer

### Account
Before you can interact with any mmL-multiplayer server, you have to create an account. You need one for each independent server. For this you have to send a request to the server with your preferred username and your public key.

### Create a game
You just have to define some settings and you are good to go.

### Join a game
The game key (a 6-digit number) is required to join a game. You may get the game code from the host or the public games list.

### Encryption
All data between the clients and the server are encrypted with RSA. To allow new players to understand the game there's no end to end encryption.

## Multiplayer Server

### Setup
nginx as well as bash is required for multiplayer_server to work correctly. Please define the two variables (provider & setup) at the top of the file. The RSA-keys are created on the first execution.

## File manipulation

### Directory creation
By using 'create_directories' it is possible to create all directories that are required for the specified path.

### Standard directories
The file-library automatically uses the correct directory depending on the operating system

## Dependencies
Some functions require 
- 'os' (mrandom/multiplayer_server/file), 
- 'base64' (mencryption/multiplayer), 
- 'cryptography' (mencryption/multiplayer), 
- 'json' (multiplayer/multiplayer-server), 
- 'requests' (multiplayer), 
- 'hashlib' (mencryption/mhash/multiplayer-server), 
- 'flask' (multiplayer-server), 
- 'time' (multiplayer-server),
- 'pathlib' (file),
- 'time' (multiplayer-server),
- 'ast' (multiplayer-server),
- 'logging' (multiplayer-server),
- 'gunicorn' (multiplayer-server)
