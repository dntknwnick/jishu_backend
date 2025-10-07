import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Service URLs
    AUTH_SERVICE_URL = app.config['AUTH_SERVICE_URL']
    USER_SERVICE_URL = app.config['USER_SERVICE_URL']
    
    def make_service_request(service_url, endpoint, method='GET', data=None, headers=None):
        """Helper function to make requests to microservices"""
        try:
            url = f"{service_url}{endpoint}"

            if headers is None:
                headers = {'Content-Type': 'application/json'}

            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return None

            return response
        except requests.exceptions.RequestException as e:
            return None

    # API Routes (Proxy to microservices)
    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        response = make_service_request(AUTH_SERVICE_URL, '/register', 'POST', data)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        response = make_service_request(AUTH_SERVICE_URL, '/login', 'POST', data)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/api/auth/google', methods=['POST'])
    def api_google_auth():
        data = request.get_json()
        response = make_service_request(AUTH_SERVICE_URL, '/google-auth', 'POST', data)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/api/auth/verify-token', methods=['POST'])
    def api_verify_token():
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Authorization token required'}), 401

        token = auth_header.split(' ')[1]
        headers = {'Authorization': f'Bearer {token}'}
        response = make_service_request(AUTH_SERVICE_URL, '/verify-token', 'POST', headers=headers)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/auth/google/callback', methods=['GET'])
    def google_oauth_callback():
        """Google OAuth callback endpoint - proxies to auth service"""
        response = make_service_request(AUTH_SERVICE_URL, '/auth/google/callback', 'GET')

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/api/user/profile', methods=['GET', 'PUT'])
    def api_user_profile():
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Authorization token required'}), 401

        headers = {'Authorization': auth_header}

        if request.method == 'GET':
            response = make_service_request(USER_SERVICE_URL, '/profile', 'GET', headers=headers)
        else:  # PUT
            data = request.get_json()
            response = make_service_request(USER_SERVICE_URL, '/profile', 'PUT', data, headers)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/api/user/change-password', methods=['POST'])
    def api_change_password():
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Authorization token required'}), 401

        headers = {'Authorization': auth_header}
        data = request.get_json()
        response = make_service_request(USER_SERVICE_URL, '/change-password', 'POST', data, headers)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/api/admin/users', methods=['GET'])
    def api_admin_users():
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Authorization token required'}), 401

        headers = {'Authorization': auth_header}

        # Forward query parameters
        query_params = request.args.to_dict()
        endpoint = '/users'
        if query_params:
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            endpoint += f"?{query_string}"

        response = make_service_request(USER_SERVICE_URL, endpoint, 'GET', headers=headers)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503

    @app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
    def api_admin_update_user_status(user_id):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Authorization token required'}), 401

        headers = {'Authorization': auth_header}
        data = request.get_json()
        response = make_service_request(USER_SERVICE_URL, f'/users/{user_id}/status', 'PUT', data, headers)

        return jsonify(response.json() if response else {'success': False, 'message': 'Service unavailable'}), \
               response.status_code if response else 503
    
    @app.route('/health')
    def health_check():
        return jsonify({'success': True, 'message': 'Gateway service is running'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Gateway is the only service exposed publicly on localhost:5000
    app.run(host='0.0.0.0', port=5000, debug=True)
