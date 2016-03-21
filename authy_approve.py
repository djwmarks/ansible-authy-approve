#!/usr/bin/python

import requests
import time

BASE_URL = "https://api.authy.com/onetouch"

def approval_request_create(authy_id, params):
    url = "%s/json/users/%d/approval_requests" % (BASE_URL, authy_id)
    res = requests.post(url, params=params)
    return res.json()

def approval_request_status(api_key, uuid):
    url = "%s/json/approval_requests/%s" % (BASE_URL, uuid)
    return requests.get(url, params=dict(api_key=api_key)).json()

def make_params(api_key, details, message):
    params = dict(
        api_key=api_key,
        message=message
    )
    params.update({ "details[%s]" % k: v for k, v in details.iteritems() })
    return params

def main():
    module = AnsibleModule(
        argument_spec = dict(
            api_key = dict(required=True, type="str"),
            approvers = dict(required=True, type="list"),
            message = dict(required=True, type="str"),
            details = dict(required=False, type="dict"),
            wait = dict(required=False, default=30, type="int")
        )
    )

    api_key = module.params["api_key"]

    uuid_list = []
    for approver in module.params["approvers"]:
        res = approval_request_create(approver["authy_id"],
                make_params(api_key, module.params["details"], module.params["message"]))
        if res["success"] == True:
            uuid_list.append(res["approval_request"]["uuid"])
        else:
            return module.fail_json(msg="Authy API failure.")

    start = time.time()
    wait = module.params["wait"]

    while True:
        for uuid in uuid_list:
            if (time.time() - start) > wait:
                return module.fail_json(msg="Approval timeout")
            res = approval_request_status(api_key, uuid)
            if res["success"] == True:
                status = res["approval_request"]["status"]
                if status == "approved":
                    return module.exit_json(changed=False, approval=res)
                elif status == "denied":
                    return module.fail_json(msg="Approval denied.")
            else:
                return module.fail_json(msg="Authy API failure.")
        time.sleep(2)

from ansible.module_utils.basic import *

if __name__ == "__main__":
    main()
