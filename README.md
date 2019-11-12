## Dynamite Configurations and Mirrors

Dynamite NSM relies on several default configurations to setup new environments from the start.

These configurations are hosted on S3, but managed within this repository.

#### S3 Staging URLs

##### [Dynamite Pro Default Configs](https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-pro/latest/default_configs.tar.gz)
##### [Dynamite Pro Mirrors](https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-pro/latest/mirrors.tar.gz)
##### [Dynamite Public Default Configs](https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-public/latest/default_configs.tar.gz)
##### [Dynamite Public Mirrors](https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-public/latest/mirrors.tar.gz)

### Deploying New Configurations/Mirrors

- Install Required Libraries

```bash
pip -r requirements.txt
```

- Copy config.cfg.example to config.cfg, and edit authentication values.

```bash
cp config.cfg.example config.cfg
vim config.cfg
```

- Note the corresponding release value in [dynamite-nsm releases](https://github.com/DynamiteAI/dynamite-nsm/releases).

<p align="center">
  <img src="https://github.com/DynamiteAI/dynamite-nsm-configurations/raw/master/img/get-dynamite-version.png"  width="90%" height="auto">
</p>


- Create a corresponding release in this repository. If you are building from the "dynamite-pro" branch, tag the version with `pro`.

- Run the deployment script
```bash
python deploy-configs.py default_configs/ mirrors/ 0.5.5
``` 

- *OR* if you are deploying as to the pro staging environment.
```bash
python deploy-configs.py default_configs/ mirrors/ 0.5.5 --dynamite-pro
```

