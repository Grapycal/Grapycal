from typing import Any, Dict
from grapycal.sobjects.controls.control import Control
from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic, GenericTopic, FloatTopic


class TextControl(Control):
    frontend_type = 'TextControl'
    def pre_build(self, attribute_values: Dict[str, Any] | None, **_):
        super().pre_build(attribute_values, **_)
        self.text = self.add_attribute('text', StringTopic, '')
        