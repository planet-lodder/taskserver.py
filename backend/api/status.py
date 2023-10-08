# Declare the HTTP routes to expose to the web server
# routes = {
#     "GET": {
#         '^/api/?$': GetStatus,
#     }
# }

from anyserver import WebRouter

# Create decorator for registering web routes
router = WebRouter('/api')


@router.get('')
def GetStatus(req, resp):
    # Set the response headers and status code
    resp.status = 200
    resp.head['content-type'] = 'application/json'

    # Return the body of the response (encoding done by router)
    return {
        "status": "online",
    }
