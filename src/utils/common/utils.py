import os
from argon2 import PasswordHasher, Type
from src.utils.common import constants
import string
import random
import json

def get_domain_name():
    environment = os.getenv("ENVIRONMENT")
    if environment in ["dev", "Dev"]:
        domain = "dev-so.zenarate.com"
    elif environment in ["qa", "Qa"]:
        domain = "qa.zenarate.com"
    elif environment in ["beta", "Beta"]:
        domain = "beta.zenarate.com"
    elif environment in ["prod", "Prod"]:
        domain = "app.zenarate.com"
    else:
        domain = "127.0.0.1:5005"
    return domain

    
def get_brand_domain(domain_name=None):
    generated_url = ""
    if domain_name:
        generated_url = constants.BASE_URL.format(domain_name)
    else:
        generated_url = constants.BASE_URL.format(get_domain_name())
    return generated_url
    

def get_stories_sharedstories_redirect_url(domain=None, data={}):
    '''Only focus on video_id for my_stories and shared_stories urls. There is no use of guide_id as of now.'''
    domain_base_url = get_brand_domain(domain_name=domain)
    story_id = data.get("story_id")
    mode = "guide" if data.get("guide_id") else "current"
    guide_id = data.get("guide_id")
    video_id = data.get("video_id")
    assignment_id = data.get("assignment_id") or 0

    detail_page_url = domain_base_url

    if video_id:
        detail_page_url += "?r=video/view&id={}&storyId={}&mode={}&source={}&assignmentId={}".format(video_id, story_id, "current", "home", assignment_id)
    else:
        detail_page_url += "?r=video/view&storyId={}&mode={}&source={}&assignmentId={}&noVideo=1".format(story_id, "current", "home", assignment_id)

    return detail_page_url
    


def get_library_redirect_url(domain=None, data={}):
    '''Show best practice story for library if available.'''
    detail_page_url = None
    domain_base_url = get_brand_domain(domain_name=domain)
    story_topic_id = data.get("story_topic_id")
    guide_id = data.get("guide_id")
    assignment_id = data.get("assignment_id") or 0
    entity_type = data.get("entity_type")
    if data.get("type") in ["Story"]:
        if guide_id:
            detail_page_url = domain_base_url + "?r=video/view&id={}&storyId={}&mode=guide&source=library&assignmentId={}".format(guide_id, story_topic_id, assignment_id)
        else:
            detail_page_url = domain_base_url + "?r=video/view&storyId={}&mode=guide&assignmentId={}&source=library&noVideo=1".format(story_topic_id, assignment_id)
    else:
        detail_page_url = domain_base_url + "?r=section/index&topicId={}".format(story_topic_id)
    if entity_type in ['T']:
        story_topic_id = data.get("story_id") or data.get("story_topic_id")
        assignment_id = data.get("assignment_id")
        if assignment_id:
            detail_page_url = domain_base_url + "?r=section/index&topicId={}&assignmentId={}".format(story_topic_id, assignment_id)
        else:
            detail_page_url = domain_base_url + "?r=section/index&topicId={}".format(story_topic_id)
        
    return detail_page_url
    


def get_todolist_redirect_url(domain=None, data={}):
    detail_page_url = None
    domain_base_url = get_brand_domain(domain_name=domain)
    story_topic_id = data.get("story_topic_id")
    story_id = data.get("story_id")
    topic_id = 0
    guide_id = data.get("guide_id") or 0
    assignment_id = data.get("assignment_id") or 0
    table_name = data.get("table_name")
    sub_section_id = data.get("sub_section_id")
    section_id = data.get("section_id")
    if table_name in ["story", "Story"]:
        if guide_id:
            detail_page_url = domain_base_url + "?r=video/view&storyId={}&mode=guide&source=home&id={}&assignmentId={}".format(story_id, guide_id, assignment_id)
        else:
            detail_page_url = domain_base_url + "?r=video/view&storyId={}&mode=guide&source=home&noVideo=1&assignmentId={}".format(story_id, assignment_id)
    else:
        topic_id = story_topic_id
        if guide_id:
            if sub_section_id:
                detail_page_url = domain_base_url + "?r=video/view&storyId={}&mode=guide&source=home&id={}&assignmentId={}&topicId={}&sectionId={}&subSectionId={}".format(story_id, guide_id, assignment_id, topic_id, section_id, sub_section_id)
            else:
                detail_page_url = domain_base_url + "?r=video/view&storyId={}&mode=guide&source=home&id={}&assignmentId={}&topicId={}&sectionId={}".format(story_id, guide_id, assignment_id, topic_id, section_id)
        else:
            if sub_section_id:
                detail_page_url = domain_base_url + "?r=video/view&storyId={}&mode=guide&source=home&noVideo=1&assignmentId={}&topicId={}&sectionId={}&subSectionId={}".format(story_id, assignment_id, topic_id, section_id, sub_section_id)
            else:
                detail_page_url = domain_base_url + "?r=video/view&storyId={}&mode=guide&source=home&noVideo=1&assignmentId={}&topicId={}&sectionId={}".format(story_id, assignment_id, topic_id, section_id)

    return detail_page_url


def pwd_hasher(pwd):
    '''Using argon2-cffi for pwd hashing:: Reason: Php is using same(Algo=Argon2ID)'''
    try:
        ph = PasswordHasher(type=Type.ID)
        hashed_pwd = ph.hash(pwd)
        return hashed_pwd
    except Exception as e:
            raise e
    

def chcek_str_with_special_chars(str_val: str):
    flag=False
    input_values = string.ascii_lowercase + string.ascii_uppercase + "_- "
    for char in str_val:
        if char not in input_values:
            flag=True
    return flag


def get_role_wise_services(role: str):
    services = []
    _role_wise_services = constants.services_assigned_to_role
    for item in _role_wise_services:
        if item == role:
            services.extend(_role_wise_services.get(item))
            break
        else:
            services.extend(_role_wise_services.get(item))
    return services


class Converter:
    @staticmethod
    def to_int(val):
        try:
            return int(val)
        except Exception as e:
            raise e
        

def get_cookie_by_value(request, key: str):
    custom_cookies_str = request.headers.get("x-custom-cookies")
    if custom_cookies_str:
        custom_cookies_json = cookie_parser(custom_cookies_str)
        cookie_val = request.cookies.get(key) if request.cookies.get(key) else custom_cookies_json.get(key)
    else:
        cookie_val = request.cookies.get(key)
    return cookie_val


def cookie_parser(cookie_string):
    cookie_dict = {}
    for chunk in cookie_string.split(";"):
        if "=" in chunk:
            key, val = chunk.split("=", 1)
        else:
            key, val = "", chunk
        key, val = key.strip(), val.strip()
        if key or val:
            cookie_dict[key] = val
    return cookie_dict


def get_story_status(key=None):
    mappings = constants.story_status_mappings
    return mappings.get(key)

def get_filtered_integer_list(lst):
    """ Return Filtered list that contains only positive Integers."""
    filtered_list = list(filter(lambda x: type(x) == int and x>0, lst))
    return filtered_list


def generate_random_string(str_len=64):
    input_values = string.ascii_lowercase + string.ascii_uppercase + string.ascii_uppercase + "_-"
    rand_value = ''
    for _ in range(str_len):
        rand_value += str(random.choice(input_values))
    return rand_value

def json_to_dict(_json=None):
    """ Convert Json To Dict."""
    try:
        json_dict = json.loads(_json)
        return json_dict
    except Exception as e:
        raise e


def dict_to_json(_dict=None):
    " Convert Dict to Json."
    try:
        dict_json = json.dumps(_dict)
        return dict_json
    except Exception as e:
        raise e

def sql_obj_to_dict(object=None):
    _dict = {}
    for key in object.__mapper__.c.keys():
        _dict[key] = getattr(object, key)
    return _dict

def get_env_name():
    """ Reads Environment Name From .env and returns it."""
    environment = os.getenv("ENVIRONMENT")
    return environment

sql_cheats = ["or 1=1","or 1=1--", "or 1=2--", "or 1=1 --",  "or 1=2 --", "' --", "or 1=1/*", "' #","'/*","' or '1'='1","' or '1'='1'--",
              "and 1=1","and 1=1--", "and 1=1 --", "and 1=2--",  "and 1=2 --", "' --", "or 1=1/*", "' #","'/*","' and '1'='1","' and '1'='1'--",
              "' or '1'='1'#", "' or '1'='1'/*", "'or 1=1 or '' or 1=1", "' or 1=1--", "' or 1=1#",
              "' or 1=1/*","') or ('1'='1", "') or ('1'='1'--", "') or ('1'='1'#", "') or ('1'='1'/*",
              "') or '1'='1", "') or '1'='1'--", "') or '1'='1'#", "') or '1'='1'/*", '" --','" #', '"/*',
              '" or "1"="1', '" or "1"="1"--', '" or "1"="1"#', '" or "1"="1"/*', '"or 1=1 or ""="',
              '" or 1=1', '" or 1=1--', '" or 1=1#', '" or 1=1/*', '") or ("1"="1', '") or ("1"="1"--', '") or ("1"="1"#',
              '") or ("1"="1"/*', '") or "1"="1', '") or "1"="1"--', '") or "1"="1"#', '") or "1"="1"/*', "union all select null --",
              "--", "&timeout /t", "&timeout", "|timeout" , "&sleep", "|sleep", "/t"
        ]

def sqlQueryInjections(string):
    # string = string.replace("\\", "")
    #string = string.encode("unicode_escape").decode()
    #string = string.encode("ascii", "ignore").decode()
    # string = re.sub(r"[\x00-\x1F\x7F]", "", string)
    # string = re.sub(r"[0-9][=][0-9]", "", string)
    # for cheat in sql_cheats:
    #     string = string.replace(cheat, "")
    return string


def format_text(text):
  """Formats a text string by adding section headers, line breaks, and bolding for important terms.

  Args:
      text (str): The text string to be formatted.

  Returns:
      str: The formatted text string.
  """

  # Split the text into sections based on headings
  sections = text.split("\n\n")

  # Format each section
  formatted_sections = []
  for section in sections:
    lines = section.splitlines()

    # Extract section header and body
    if len(lines) >= 2:
      header = lines[0].strip()
      body = "\n".join(lines[1:])
    else:
      header = ""
      body = lines[0]

    # Format section header with bold text
    formatted_header = f"\n**{header}**\n" if header else ""

    # Format body with line breaks
    formatted_body = body.replace("\n", "\n  ")

    # Combine formatted header and body
    formatted_sections.append(formatted_header + formatted_body)

  # Join all formatted sections with a single newline
  return ".".join(formatted_sections)