"""
Unit tests for course and subject management endpoints
"""

import pytest
import json

from shared.models.course import ExamCategory, ExamCategorySubject
from tests.conftest import assert_success_response, assert_error_response


class TestCourseEndpoints:
    """Test course management endpoints"""
    
    def test_get_courses_public(self, client, sample_course):
        """Test getting courses list (public endpoint)"""
        response = client.get('/api/courses')
        
        data = assert_success_response(response)
        assert 'courses' in data['data']
        assert 'pagination' in data['data']
        assert len(data['data']['courses']) >= 1
        
        # Check course structure
        course = data['data']['courses'][0]
        assert 'id' in course
        assert 'course_name' in course
        assert 'amount' in course
        assert 'offer_amount' in course
    
    def test_get_courses_with_pagination(self, client, sample_course):
        """Test courses pagination"""
        response = client.get('/api/courses?page=1&per_page=5')
        
        data = assert_success_response(response)
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['per_page'] == 5
        assert 'total' in pagination
        assert 'pages' in pagination
    
    def test_get_courses_with_search(self, client, sample_course):
        """Test courses search functionality"""
        response = client.get(f'/api/courses?search={sample_course.course_name[:5]}')
        
        data = assert_success_response(response)
        courses = data['data']['courses']
        assert len(courses) >= 1
        assert sample_course.course_name.lower() in courses[0]['course_name'].lower()
    
    def test_get_course_by_id(self, client, sample_course):
        """Test getting specific course by ID"""
        response = client.get(f'/api/courses/{sample_course.id}')
        
        data = assert_success_response(response)
        course = data['data']['course']
        assert course['id'] == sample_course.id
        assert course['course_name'] == sample_course.course_name
    
    def test_get_course_by_id_not_found(self, client):
        """Test getting non-existent course"""
        response = client.get('/api/courses/99999')
        
        assert_error_response(response, 404)
    
    def test_get_course_with_subjects(self, client, sample_course, sample_subject):
        """Test getting course with subjects included"""
        response = client.get(f'/api/courses/{sample_course.id}?include_subjects=true')
        
        data = assert_success_response(response)
        course = data['data']['course']
        assert 'subjects' in course
        assert len(course['subjects']) >= 1
        assert course['subjects'][0]['subject_name'] == sample_subject.subject_name


class TestSubjectEndpoints:
    """Test subject management endpoints"""
    
    def test_get_subjects_by_course(self, client, sample_course, sample_subject):
        """Test getting subjects for a specific course"""
        response = client.get(f'/api/subjects?course_id={sample_course.id}')
        
        data = assert_success_response(response)
        assert 'subjects' in data['data']
        subjects = data['data']['subjects']
        assert len(subjects) >= 1
        assert subjects[0]['subject_name'] == sample_subject.subject_name
        assert subjects[0]['exam_category_id'] == sample_course.id
    
    def test_get_subjects_exclude_deleted(self, client, sample_course, sample_subject, db_session):
        """Test that deleted subjects are excluded by default"""
        # Mark subject as deleted
        sample_subject.is_deleted = True
        db_session.commit()
        
        response = client.get(f'/api/subjects?course_id={sample_course.id}')
        
        data = assert_success_response(response)
        subjects = data['data']['subjects']
        # Should not include deleted subject
        assert len(subjects) == 0
    
    def test_get_subjects_include_deleted(self, client, sample_course, sample_subject, db_session):
        """Test including deleted subjects when requested"""
        # Mark subject as deleted
        sample_subject.is_deleted = True
        db_session.commit()
        
        response = client.get(f'/api/subjects?course_id={sample_course.id}&include_deleted=true')
        
        data = assert_success_response(response)
        subjects = data['data']['subjects']
        # Should include deleted subject
        assert len(subjects) >= 1
        assert subjects[0]['is_deleted'] is True
    
    def test_get_subjects_invalid_course(self, client):
        """Test getting subjects for non-existent course"""
        response = client.get('/api/subjects?course_id=99999')
        
        data = assert_success_response(response)
        assert len(data['data']['subjects']) == 0


class TestBundleEndpoints:
    """Test bundle management endpoints"""
    
    def test_get_bundles_by_course(self, client, sample_course, sample_bundle):
        """Test getting bundles for a specific course"""
        response = client.get(f'/api/bundles?course_id={sample_course.id}')
        
        data = assert_success_response(response)
        assert 'bundles' in data['data']
        bundles = data['data']['bundles']
        assert len(bundles) >= 1
        assert bundles[0]['is_bundle'] is True
        assert bundles[0]['subject_name'] == sample_bundle.subject_name
    
    def test_get_bundles_exclude_regular_subjects(self, client, sample_course, sample_subject, sample_bundle):
        """Test that regular subjects are not included in bundles"""
        response = client.get(f'/api/bundles?course_id={sample_course.id}')
        
        data = assert_success_response(response)
        bundles = data['data']['bundles']
        
        # Should only include bundle subjects
        for bundle in bundles:
            assert bundle['is_bundle'] is True
    
    def test_get_bundles_exclude_deleted(self, client, sample_course, sample_bundle, db_session):
        """Test that deleted bundles are excluded"""
        # Mark bundle as deleted
        sample_bundle.is_deleted = True
        db_session.commit()
        
        response = client.get(f'/api/bundles?course_id={sample_course.id}')
        
        data = assert_success_response(response)
        bundles = data['data']['bundles']
        # Should not include deleted bundle
        assert len(bundles) == 0


class TestAdminCourseManagement:
    """Test admin course management endpoints"""
    
    def test_admin_get_courses(self, client, admin_auth_headers, sample_course):
        """Test admin getting all courses"""
        response = client.get('/api/admin/courses', headers=admin_auth_headers)
        
        data = assert_success_response(response)
        assert 'courses' in data['data']
        assert len(data['data']['courses']) >= 1
    
    def test_admin_create_course(self, client, admin_auth_headers, valid_course_data, db_session):
        """Test admin creating new course"""
        response = client.post('/api/admin/courses', 
                             headers=admin_auth_headers, json=valid_course_data)
        
        data = assert_success_response(response, 201)
        assert 'course' in data['data']
        course = data['data']['course']
        assert course['course_name'] == valid_course_data['course_name']
        assert course['amount'] == valid_course_data['amount']
        
        # Verify in database
        db_course = db_session.query(ExamCategory).filter_by(
            course_name=valid_course_data['course_name']
        ).first()
        assert db_course is not None
    
    def test_admin_create_course_invalid_data(self, client, admin_auth_headers):
        """Test admin creating course with invalid data"""
        invalid_data = {
            'course_name': '',  # Empty name
            'amount': -100,     # Negative amount
            'max_tokens': 'invalid'  # Invalid type
        }
        
        response = client.post('/api/admin/courses', 
                             headers=admin_auth_headers, json=invalid_data)
        
        assert_error_response(response, 400)
    
    def test_admin_update_course(self, client, admin_auth_headers, sample_course, db_session):
        """Test admin updating existing course"""
        update_data = {
            'course_name': 'Updated Course Name',
            'description': 'Updated description',
            'offer_amount': 699.00
        }
        
        response = client.put(f'/api/admin/courses/{sample_course.id}', 
                            headers=admin_auth_headers, json=update_data)
        
        data = assert_success_response(response)
        course = data['data']['course']
        assert course['course_name'] == update_data['course_name']
        assert course['offer_amount'] == update_data['offer_amount']
        
        # Verify in database
        db_session.refresh(sample_course)
        assert sample_course.course_name == update_data['course_name']
    
    def test_admin_delete_course(self, client, admin_auth_headers, sample_course, db_session):
        """Test admin deleting course"""
        response = client.delete(f'/api/admin/courses/{sample_course.id}', 
                               headers=admin_auth_headers)
        
        data = assert_success_response(response)
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify course is deleted from database
        db_course = db_session.query(ExamCategory).filter_by(id=sample_course.id).first()
        assert db_course is None
    
    def test_non_admin_cannot_manage_courses(self, client, auth_headers, valid_course_data):
        """Test that non-admin users cannot manage courses"""
        response = client.post('/api/admin/courses', 
                             headers=auth_headers, json=valid_course_data)
        
        assert_error_response(response, 403)


class TestAdminSubjectManagement:
    """Test admin subject management endpoints"""
    
    def test_admin_create_subject(self, client, admin_auth_headers, sample_course, valid_subject_data, db_session):
        """Test admin creating new subject"""
        valid_subject_data['course_id'] = sample_course.id
        
        response = client.post('/api/admin/subjects', 
                             headers=admin_auth_headers, json=valid_subject_data)
        
        data = assert_success_response(response, 201)
        subject = data['data']['subject']
        assert subject['subject_name'] == valid_subject_data['subject_name']
        assert subject['exam_category_id'] == sample_course.id
        
        # Verify in database
        db_subject = db_session.query(ExamCategorySubject).filter_by(
            subject_name=valid_subject_data['subject_name']
        ).first()
        assert db_subject is not None
    
    def test_admin_create_duplicate_subject(self, client, admin_auth_headers, sample_course, sample_subject):
        """Test admin creating duplicate subject in same course"""
        duplicate_data = {
            'course_id': sample_course.id,
            'subject_name': sample_subject.subject_name,  # Same name
            'amount': 299.00,
            'offer_amount': 199.00,
            'max_tokens': 200,
            'total_mock': 25
        }
        
        response = client.post('/api/admin/subjects', 
                             headers=admin_auth_headers, json=duplicate_data)
        
        assert_error_response(response, 400)
    
    def test_admin_update_subject(self, client, admin_auth_headers, sample_subject, db_session):
        """Test admin updating existing subject"""
        update_data = {
            'subject_name': 'Updated Subject Name',
            'amount': 399.00,
            'total_mock': 30,
            'is_deleted': False
        }
        
        response = client.put(f'/api/admin/subjects/{sample_subject.id}', 
                            headers=admin_auth_headers, json=update_data)
        
        data = assert_success_response(response)
        subject = data['data']['subject']
        assert subject['subject_name'] == update_data['subject_name']
        assert subject['amount'] == update_data['amount']
        
        # Verify in database
        db_session.refresh(sample_subject)
        assert sample_subject.subject_name == update_data['subject_name']
    
    def test_admin_soft_delete_subject(self, client, admin_auth_headers, sample_subject, db_session):
        """Test admin soft deleting subject"""
        update_data = {'is_deleted': True}
        
        response = client.put(f'/api/admin/subjects/{sample_subject.id}', 
                            headers=admin_auth_headers, json=update_data)
        
        data = assert_success_response(response)
        assert data['data']['subject']['is_deleted'] is True
        
        # Verify in database
        db_session.refresh(sample_subject)
        assert sample_subject.is_deleted is True
    
    def test_admin_restore_deleted_subject(self, client, admin_auth_headers, sample_subject, db_session):
        """Test admin restoring soft deleted subject"""
        # First soft delete
        sample_subject.is_deleted = True
        db_session.commit()
        
        # Then restore
        update_data = {'is_deleted': False}
        response = client.put(f'/api/admin/subjects/{sample_subject.id}', 
                            headers=admin_auth_headers, json=update_data)
        
        data = assert_success_response(response)
        assert data['data']['subject']['is_deleted'] is False
        
        # Verify in database
        db_session.refresh(sample_subject)
        assert sample_subject.is_deleted is False
    
    def test_non_admin_cannot_manage_subjects(self, client, auth_headers, sample_course, valid_subject_data):
        """Test that non-admin users cannot manage subjects"""
        valid_subject_data['course_id'] = sample_course.id
        
        response = client.post('/api/admin/subjects', 
                             headers=auth_headers, json=valid_subject_data)
        
        assert_error_response(response, 403)


class TestCourseValidation:
    """Test course and subject validation"""
    
    def test_course_name_validation(self, client, admin_auth_headers):
        """Test course name validation"""
        test_cases = [
            ('', 'Empty name'),
            ('A', 'Too short'),
            ('A' * 101, 'Too long'),
            ('Valid Course Name', 'Valid name')
        ]
        
        for name, description in test_cases:
            course_data = {
                'course_name': name,
                'description': 'Test description',
                'amount': 999.00,
                'offer_amount': 799.00,
                'max_tokens': 1000
            }
            
            response = client.post('/api/admin/courses', 
                                 headers=admin_auth_headers, json=course_data)
            
            if description == 'Valid name':
                assert response.status_code in [200, 201]
            else:
                assert response.status_code == 400
    
    def test_pricing_validation(self, client, admin_auth_headers):
        """Test pricing validation"""
        test_cases = [
            (-100, 'Negative amount'),
            (0, 'Zero amount'),
            (999.99, 'Valid amount'),
            ('invalid', 'Invalid type')
        ]
        
        for amount, description in test_cases:
            course_data = {
                'course_name': 'Test Course',
                'description': 'Test description',
                'amount': amount,
                'offer_amount': 799.00,
                'max_tokens': 1000
            }
            
            response = client.post('/api/admin/courses', 
                                 headers=admin_auth_headers, json=course_data)
            
            if description == 'Valid amount':
                assert response.status_code in [200, 201]
            else:
                assert response.status_code == 400
    
    def test_token_validation(self, client, admin_auth_headers):
        """Test token count validation"""
        test_cases = [
            (-1, 'Negative tokens'),
            (0, 'Zero tokens (unlimited)'),
            (1000, 'Valid tokens'),
            ('invalid', 'Invalid type')
        ]
        
        for tokens, description in test_cases:
            course_data = {
                'course_name': 'Test Course',
                'description': 'Test description',
                'amount': 999.00,
                'offer_amount': 799.00,
                'max_tokens': tokens
            }
            
            response = client.post('/api/admin/courses', 
                                 headers=admin_auth_headers, json=course_data)
            
            if description in ['Zero tokens (unlimited)', 'Valid tokens']:
                assert response.status_code in [200, 201]
            else:
                assert response.status_code == 400
