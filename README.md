## Getting started contributing
* First of all clone repository.  
  ```bash
  $ git clone --recursive https://github.com/absortium/deluge.git
  ```

* Go into `useful` directory and copy `deluge`,`docker` and `docker-compose` aliases to your alias file.
  * `zsh` - `~/.zsh_aliases`
  * `bash` - `~/.bash_aliases`
 
* Set environment variables.
  * `export DELUGE_PATH='YOUR_WORK_DIRECTORY_PATH'` 
  * `export DEFAULT_MODE='unit'`

* Add entry to the `/etc/hosts`
   * If you run docker containers on the `docker-machine`, than check your `docker-machine` ip and pass it to the `/etc/hosts`
   ```
   $ docker-machine ip
   $ sudo bash -c `echo "absortium.com <ip>" >> /etc/hosts`
   ```
   * Otherwise set localhost
   ```
   $ sudo bash -c `echo "absortium.com localhost" >> /etc/hosts`
   ```
   
* Open new terminal and go into docker `dev` directory, if there is no such alias than you should check - `Are aliases were preloaded?`
  ```
  $ godd
  ```

* Run `postgres` service which serve as database.
  ```
  $ dc up -d postgres
  ```
* Migrate `m-backend` database.
  ```
  $ dc run m-ethwallet migrate
  ```  
* Run `ethwallet` tests.
  ```
  $ dc run m-ethwallet test --verbosity 2 ethwallet.tests.unit
  ```

    
## Tips
* If you use `docker-machine` than you must download project only in user directory.
 
## Services
* `m-ethwallet` - main ethwallet service.
* `w-ethwallet` - ethwallet worker service (celery).
* `frontend` - frontend service.
* `postgres` - postgres service (postgres data are stored separately, even if you remove service the data would be persisted).
* `rabbitmq` - queue service.
* `redis` - redis service (needed as backend for `rabbitmq` tasks store).
* `ethnode` - go client docker service with turned on RPC support.

## Alias info
* `god` - go to the `DELUGE_PATH` directory.
* `godd` - go to the `docker` dev directory (in order to run docker service)
* `gods` - go to the `services` directory.
* `gods <service>` - go to the `<service>` project directory.
* `dcinit <mode>` - init start mode, default mode is `DEFAULT_MODE` .
    * `frontend`
        * external systems like `coinbase` and `ethwallet` are mocked.
        * `postgres`, `rabbitmq`, `celery`, `router` services are required to be up in order to celery task work.
        * celery workers are working and celery tasks are executing like in real system.
        * (NOT EXIST YET) special service `walletnotifier` is working and emulating money notification from `coinbase` and `ethwallet` 
    * (for more information please read `README.md` in the `docker` directory)         
   
* `dc(b| build) <service>` - build service.
* `dc(r| run) <service>` - run service.
* `drmc <regex>` - delete containers that much regex expression.
* `drmi <regex>` - delete images that much regex expression.
* `dc(l| logs) <service>` - output service logs.
* `di` - list all images.
* `dps` - list all working containers.
* `ideluge` - init sensitive information that is needed for backend start.


