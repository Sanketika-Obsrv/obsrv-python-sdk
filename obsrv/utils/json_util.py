import json


class JSONUtil:  # pragma: no cover
    @staticmethod
    def serialize(obj):
        if isinstance(obj, str):
            return obj
        else:
            return json.dumps(obj, default=str)

    @staticmethod
    def deserialize(json_str):
        return json.loads(json_str)

    @staticmethod
    def get_json_type(json_str):
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                return "ARRAY"
            elif isinstance(data, dict):
                return "OBJECT"
            else:
                return "NOT_A_JSON"
        except json.JSONDecodeError:
            return "NOT_A_JSON"
