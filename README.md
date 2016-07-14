    Branch  | Status 
  --------| -------
  master | [![Build Status](https://travis-ci.org/absortium/ethwallet.svg?branch=master)](https://travis-ci.org/absortium/ethwallet)
  development | [![Build Status](https://travis-ci.org/absortium/ethwallet.svg?branch=development)](https://travis-ci.org/absortium/ethwallet)


## Getting started  
#### Prerequisites
  
    Name  | Version 
  --------|---------
  docker-compose | 1.8.0-rc1
  docker | 1.12.0-rc3
  
  **Step №1**: Clone repository.  
  ```bash
  $ git clone --recursive https://github.com/absortium/deluge.git
  $ cd deluge
  ```

  **Step №2**: Ask maintainer to give you `.sensitive` file.
  
  **Step №3**: Install `ethwallet` and run tests.
  ```bash
  $ ./useful/install.sh ethwallet
  ```
 
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
* `godd` - go to the `docker` directory.
* `gods` - go to the `services` directory.
* `gods <backend|frontend|ethwallet|router|ethnode>` - go to the `service` project directory.
* `di` - list all images.
* `dps` - list all working containers.
* `dcinit <unit|integration|frontend|testnet>` - init start mode, default mode is `DEFAULT_MODE` .
    * `frontend`
        * external systems like `coinbase` and `ethwallet` are mocked.
        * `postgres`, `rabbitmq`, `celery`, `router` services are required to be up in order to celery task work.
        * celery workers are working and celery tasks are executing like in real system.
        * Service `notifier` is working and emulating money notification from `coinbase` and `ethwallet`.
    * (for more information please read `README.md` in the `docker` directory)         

* `dc` - alias for `docker-compose -f $DELUGE_PATH/docker/images/dev.yml -f $DELUGE_PATH/docker/composes/frontend.yml`.
* `dc(b| build) <service>` - build service.
* `dc(r| run) <service>` - run service.
* `dc(u| up) <service>` - up service.
* `dc(l| logs) <service>` - output service logs.
* `drmc <regex>` - delete containers that much regex expression.
* `drmi <regex>` - delete images that much regex expression.
* `drmd <regex>` - delete volumes that much regex expression.


