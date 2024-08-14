import datetime
import random
import string


char_rand_options = string.digits + string.ascii_lowercase + string.ascii_uppercase
char_rand_options_lower = string.ascii_lowercase


def generate_id_with_prefix(prefix, scope=None, length=4, separator="", only_lower=False):
    created_at = datetime.datetime.utcnow()
    options = char_rand_options_lower if only_lower else char_rand_options
    parts = [prefix]
    if scope:
        parts.append(scope)
    parts.append(created_at.strftime("%y%m%d%H%M%S"))
    parts.append("".join(random.choice(options) for i in range(length)))
    return separator.join(parts)


def simple_id_generator(salt, parts=2, prefix=None):
    id_parts = [str(random.randint(0, 999)) for i in range(parts)]
    if prefix:
        id_parts.insert(0, prefix)
    id_parts.append(str(salt))
    return "-".join(id_parts)


def simple_prefix_id_generator(prefix):
    return "{}-{}".format(prefix, random.randint(0, 999))


def extract_id_salt(id):
    id_parts = id.split("-")
    if len(id_parts) > 0:
        return int(id_parts[-1])
    else:
        return None


def get_next_entity_id(entity_list):
    return len(entity_list) + 1 if entity_list else 1
