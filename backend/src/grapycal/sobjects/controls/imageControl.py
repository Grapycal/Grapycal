import io
from typing import Any, Dict
from grapycal.sobjects.controls.control import Control
from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic, GenericTopic, FloatTopic

smallest_jpg = '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k='

class ImageControl(Control):
    '''
    '''
    frontend_type = 'ImageControl'
    def pre_build(self, attribute_values: Dict[str, Any] | None,**_):
        super().pre_build(attribute_values, **_)
        self.image = self.add_attribute('image', StringTopic,smallest_jpg)
    
    def set_image(self,image:bytes|io.BytesIO):
        if isinstance(image,io.BytesIO):
            image.seek(0)
            image = image.read()
        self.image.set_from_binary(image)
        