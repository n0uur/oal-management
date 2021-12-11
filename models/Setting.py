from inspect import Attribute
from pynamodb.models import Model
import pynamodb.attributes as Attributes
import os

if __name__ == "__main__":
    """debugging"""

    from dotenv import load_dotenv

    load_dotenv()

class Setting(Model):
    class Meta:
        table_name = os.environ.get("DATABASE_SETTING_TABLE", 'g5_settings')
        region = os.environ.get("DATABASE_REGION", 'us-east-1')

        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY")
        aws_secret_access_key = os.environ.get("AWS_SECRET_KEY")

    id = Attributes.UnicodeAttribute(hash_key=True)
    value = Attributes.UnicodeAttribute()

    @classmethod
    def get(cls, key, default=None, dataType=None):
        try:
            value = super().get(key).value
            if dataType is None:
                return value
            return dataType(value)
        except:
            return default

    @classmethod
    def set(cls, key, value):
        try:
            Setting(key, value=str(value)).save()
            return value
        except:
            return None


if __name__ == "__main__":
    """debugging"""
    
    print(type(Setting.get("hi", dataType=bool)))

