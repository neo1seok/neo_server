
import yaml

with open('config.yaml') as f:
    conf = yaml.safe_load(f)

print(conf)

language = conf['language']
test = conf['pytest']