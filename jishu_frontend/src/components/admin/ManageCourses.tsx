import { useState, useEffect } from 'react';
import Header from '../Header';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Checkbox } from '../ui/checkbox';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';

import {
  Plus,
  Edit2,
  Trash2,
  Search,
  BookOpen,
  Users,
  DollarSign,
  Loader2,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import { toast } from 'sonner';
import { useAppDispatch, useAppSelector } from '../../store';
import { fetchCourses, createCourse, updateCourse, deleteCourse, createSubject, updateSubject, fetchSubjects } from '../../store/slices/adminSlice';

interface ManageCoursesProps {
  user: any;
}

export default function ManageCourses({ user }: ManageCoursesProps) {
  const dispatch = useAppDispatch();
  const { courses, isLoading, error } = useAppSelector((state) => state.admin);

  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<any>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [expandedCourseId, setExpandedCourseId] = useState<number | null>(null);
  const [subjectModalCourse, setSubjectModalCourse] = useState<any>(null);
  const [isSubjectDialogOpen, setIsSubjectDialogOpen] = useState(false);
  const [courseSubjects, setCourseSubjects] = useState<{[key: number]: any[]}>({});
  const [loadingSubjects, setLoadingSubjects] = useState<Set<number>>(new Set());
  const [editingSubject, setEditingSubject] = useState<any>(null);
  const [isEditSubjectDialogOpen, setIsEditSubjectDialogOpen] = useState(false);

  const [subjectFormData, setSubjectFormData] = useState({
    subject_name: '',
    amount: '',
    offer_amount: '',
    max_tokens: '',
    total_mock: '',
    is_bundle: false
  });

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    offerPrice: '',
    maxTokens: ''
  });

  const [editFormData, setEditFormData] = useState({
    name: '',
    description: '',
    price: '',
    offerPrice: '',
    maxTokens: ''
  });

  const [editSubjectFormData, setEditSubjectFormData] = useState({
    subject_name: '',
    amount: '',
    offer_amount: '',
    max_tokens: '',
    total_mock: '',
    is_bundle: false,
    is_deleted: false
  });

  useEffect(() => {
    dispatch(fetchCourses());
  }, [dispatch, user]);

  const filteredCourses = courses.filter(course =>
    // Hide soft-deleted courses from active listings
    !course.is_deleted &&
    (course.course_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    course.name?.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleCreateCourse = async () => {
    if (!formData.name?.trim()) {
      toast.error('Please fill in the course name');
      return;
    }
    if (formData.name.trim().length < 2) {
      toast.error('Course name must be at least 2 characters long');
      return;
    }
    try {
      const courseData = {
        course_name: formData.name,
        description: formData.description,
        amount: parseFloat(formData.price) || 0,
        offer_amount: parseFloat(formData.offerPrice) || 0,
        max_tokens: parseInt(formData.maxTokens) || 100
      };
      await dispatch(createCourse(courseData)).unwrap();
      setFormData({ name: '', description: '', price: '', offerPrice: '', maxTokens: '' });
      setIsCreateDialogOpen(false);
      toast.success('Course created successfully!');
    } catch (error) {
      toast.error('Failed to create course');
    }
  };

  const handleAddSubject = (course: any) => {
    setSubjectModalCourse(course);
    setIsSubjectDialogOpen(true);
  };

  const handleCreateSubject = async () => {
    if (!subjectFormData.subject_name?.trim() || !subjectModalCourse) {
      toast.error('Please fill in the subject name');
      return;
    }
    if (subjectFormData.subject_name.trim().length < 2) {
      toast.error('Subject name must be at least 2 characters long');
      return;
    }
    try {
      const subjectData = {
        course_id: subjectModalCourse.id,
        subject_name: subjectFormData.subject_name,
        amount: parseFloat(subjectFormData.amount) || 0,
        offer_amount: parseFloat(subjectFormData.offer_amount) || 0,
        max_tokens: parseInt(subjectFormData.max_tokens) || 100,
        total_mock: parseInt(subjectFormData.total_mock) || 50,
        is_bundle: subjectFormData.is_bundle
      };
      const newSubject = await dispatch(createSubject(subjectData)).unwrap();
      setCourseSubjects(prev => ({
        ...prev,
        [subjectModalCourse.id]: [...(prev[subjectModalCourse.id] || []), newSubject]
      }));
      setSubjectFormData({ subject_name: '', amount: '', offer_amount: '', max_tokens: '', total_mock: '', is_bundle: false });
      setIsSubjectDialogOpen(false);
      setSubjectModalCourse(null);
      toast.success('Subject created successfully!');
      setExpandedCourseId(subjectModalCourse.id);
    } catch (error) {
      toast.error('Failed to create subject');
    }
  };

  const toggleCourseExpansion = async (courseId: number) => {
    // If clicking on the already expanded course, collapse it
    if (expandedCourseId === courseId) {
      setExpandedCourseId(null);
      return;
    }

    // Expand the new course (this automatically collapses any previously expanded course)
    setExpandedCourseId(courseId);

    // Load subjects if not already loaded
    if (!courseSubjects[courseId]) {
      setLoadingSubjects(prev => new Set([...prev, courseId]));
      try {
        const subjects = await dispatch(fetchSubjects(courseId)).unwrap();
        setCourseSubjects(prev => ({
          ...prev,
          [courseId]: subjects
        }));
      } catch (error) {
        toast.error('Failed to load subjects');
      } finally {
        setLoadingSubjects(prev => {
          const newSet = new Set(prev);
          newSet.delete(courseId);
          return newSet;
        });
      }
    }
  };

  const handleEditCourse = (course: any) => {
    setEditingCourse(course);
    setEditFormData({
      name: course.course_name || course.name || '',
      description: course.description || '',
      price: course.amount?.toString() || '',
      offerPrice: course.offer_amount?.toString() || '',
      maxTokens: course.max_tokens?.toString() || ''
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateCourse = async () => {
    if (!editFormData.name?.trim()) {
      toast.error('Course name is required');
      return;
    }

    try {
      await dispatch(updateCourse({
        id: editingCourse.id,
        data: {
          course_name: editFormData.name.trim(),
          description: editFormData.description.trim(),
          amount: parseFloat(editFormData.price) || 0,
          offer_amount: parseFloat(editFormData.offerPrice) || 0,
          max_tokens: parseInt(editFormData.maxTokens) || 100
        }
      })).unwrap();

      toast.success('Course updated successfully!');
      setIsEditDialogOpen(false);
      setEditingCourse(null);
      setEditFormData({ name: '', description: '', price: '', offerPrice: '', maxTokens: '' });
    } catch (error) {
      toast.error('Failed to update course');
    }
  };

  const handleDeleteCourse = async (courseId: number) => {
    if (window.confirm('Are you sure you want to delete this course?')) {
      try {
        await dispatch(deleteCourse(courseId)).unwrap();
        toast.success('Course deleted successfully!');
      } catch (error) {
        toast.error('Failed to delete course');
      }
    }
  };

  const handleSoftDeleteCourse = async (courseId: number) => {
    if (window.confirm('Are you sure you want to soft delete this course? This will hide it from users but keep the data.')) {
      try {
        await dispatch(updateCourse({
          id: courseId,
          data: {
            course_name: editingCourse.course_name || editingCourse.name,
            description: editingCourse.description || '',
            amount: editingCourse.amount || 0,
            offer_amount: editingCourse.offer_amount || 0,
            max_tokens: editingCourse.max_tokens || 100,
            is_deleted: true
          }
        })).unwrap();

        toast.success('Course soft deleted successfully!');
        setIsEditDialogOpen(false);
        setEditingCourse(null);
        setEditFormData({ name: '', description: '', price: '', offerPrice: '', maxTokens: '' });
      } catch (error) {
        toast.error('Failed to soft delete course');
      }
    }
  };

  const handleEditSubject = (subject: any) => {
    setEditingSubject(subject);
    setEditSubjectFormData({
      subject_name: subject.subject_name || '',
      amount: subject.amount?.toString() || '',
      offer_amount: subject.offer_amount?.toString() || '',
      max_tokens: subject.max_tokens?.toString() || '',
      total_mock: subject.total_mock?.toString() || '',
      is_bundle: subject.is_bundle || false,
      is_deleted: subject.is_deleted || false
    });
    setIsEditSubjectDialogOpen(true);
  };

  const handleUpdateSubject = async () => {
    if (!editSubjectFormData.subject_name?.trim()) {
      toast.error('Subject name is required');
      return;
    }

    try {
      await dispatch(updateSubject({
        id: editingSubject.id,
        data: {
          subject_name: editSubjectFormData.subject_name.trim(),
          amount: parseFloat(editSubjectFormData.amount) || 0,
          offer_amount: parseFloat(editSubjectFormData.offer_amount) || 0,
          max_tokens: parseInt(editSubjectFormData.max_tokens) || 100,
          total_mock: parseInt(editSubjectFormData.total_mock) || 50,
          is_bundle: editSubjectFormData.is_bundle,
          is_deleted: editSubjectFormData.is_deleted
        }
      })).unwrap();

      toast.success('Subject updated successfully!');
      setIsEditSubjectDialogOpen(false);
      setEditingSubject(null);

      // Refresh the subjects for the course
      if (editingSubject.exam_category_id) {
        const subjects = await dispatch(fetchSubjects(editingSubject.exam_category_id)).unwrap();
        setCourseSubjects(prev => ({
          ...prev,
          [editingSubject.exam_category_id]: subjects
        }));
      }
    } catch (error) {
      toast.error('Failed to update subject');
    }
  };

  const handleSoftDeleteSubject = async (subject: any) => {
    if (window.confirm(`Are you sure you want to soft delete "${subject.subject_name}"? This will hide it from users but keep the data.`)) {
      try {
        await dispatch(updateSubject({
          id: subject.id,
          data: { is_deleted: true }
        })).unwrap();

        toast.success('Subject soft deleted successfully!');

        // Refresh the subjects for the course
        if (subject.exam_category_id) {
          const subjects = await dispatch(fetchSubjects(subject.exam_category_id)).unwrap();
          setCourseSubjects(prev => ({
            ...prev,
            [subject.exam_category_id]: subjects
          }));
        }
      } catch (error) {
        toast.error('Failed to soft delete subject');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background dark:bg-slate-900">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2 text-foreground">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading courses...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background dark:bg-slate-900">
      <Header user={user} />

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2 text-foreground">Manage Courses & Subjects</h1>
            <p className="text-xl text-muted-foreground dark:text-muted-foreground">Create and manage test courses</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button size="lg" className="gap-2">
                <Plus className="w-5 h-5" />
                Create Course
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle className="text-foreground">Create New Course</DialogTitle>
                <DialogDescription className="text-muted-foreground dark:text-muted-foreground">Add a new course or test series</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-foreground">Course Name *</Label>
                    <Input
                      id="name"
                      placeholder="e.g., NEET, JEE Advanced"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="price">Regular Price (₹)</Label>
                    <Input
                      id="price"
                      type="number"
                      placeholder="999"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="offerPrice">Offer Price (₹)</Label>
                    <Input
                      id="offerPrice"
                      type="number"
                      placeholder="799"
                      value={formData.offerPrice}
                      onChange={(e) => setFormData({ ...formData, offerPrice: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="maxTokens">Max AI Tokens</Label>
                    <Input
                      id="maxTokens"
                      type="number"
                      placeholder="100"
                      value={formData.maxTokens}
                      onChange={(e) => setFormData({ ...formData, maxTokens: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Course description..."
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateCourse}>Create Course</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Search */}
        <div className="flex items-center gap-4 mb-8">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-1">Total Courses</p>
                  <p className="text-3xl text-foreground">{filteredCourses.length}</p>
                </div>
                <BookOpen className="w-10 h-10 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-1">Total Students</p>
                  <p className="text-3xl text-foreground">{filteredCourses.reduce((sum, c) => sum + (c.students || 0), 0).toLocaleString()}</p>
                </div>
                <Users className="w-10 h-10 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-1">Total Revenue</p>
                  <p className="text-3xl text-foreground">₹{filteredCourses.reduce((sum, c) => sum + (c.amount || 0), 0).toLocaleString()}</p>
                </div>
                <DollarSign className="w-10 h-10 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Courses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCourses.map((course, index) => {
            // Color schemes for different courses
            const colorSchemes = [
              { header: 'bg-gradient-to-r from-pink-500 to-pink-600', button: 'bg-pink-500 hover:bg-pink-600', icon: 'bg-pink-100 text-pink-600' },
              { header: 'bg-gradient-to-r from-blue-500 to-blue-600', button: 'bg-blue-500 hover:bg-blue-600', icon: 'bg-blue-100 text-blue-600' },
              { header: 'bg-gradient-to-r from-purple-500 to-purple-600', button: 'bg-purple-500 hover:bg-purple-600', icon: 'bg-purple-100 text-purple-600' },
              { header: 'bg-gradient-to-r from-green-500 to-green-600', button: 'bg-green-500 hover:bg-green-600', icon: 'bg-green-100 text-green-600' },
              { header: 'bg-gradient-to-r from-orange-500 to-orange-600', button: 'bg-orange-500 hover:bg-orange-600', icon: 'bg-orange-100 text-orange-600' },
              { header: 'bg-gradient-to-r from-teal-500 to-teal-600', button: 'bg-teal-500 hover:bg-teal-600', icon: 'bg-teal-100 text-teal-600' }
            ];
            const colorScheme = colorSchemes[index % colorSchemes.length];
            const subjectCount = courseSubjects[course.id]?.length || course.subjects_count || 0;
            const testCount = subjectCount * 50; // Approximate tests per subject
            const studentCount = Math.floor(Math.random() * 20000) + 5000; // Mock student count

            return (
              <Card key={course.id} className="overflow-hidden hover:shadow-xl transition-all duration-300 group">
                {/* Colored Header */}
                <div className={`h-2 ${colorScheme.header}`}></div>

                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className={`w-16 h-16 ${colorScheme.icon} rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                      <BookOpen className="w-8 h-8" />
                    </div>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground dark:text-muted-foreground">
                      <span className="font-medium">{testCount}</span>
                      <span>Tests</span>
                    </div>
                  </div>

                  <div>
                    <CardTitle className="text-2xl mb-2 text-foreground">{course.course_name || course.name}</CardTitle>
                    <p className="text-muted-foreground dark:text-muted-foreground text-sm mb-3">{course.description}</p>

                    {/* Subject Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {courseSubjects[course.id] && courseSubjects[course.id].length > 0 ? (
                        courseSubjects[course.id].slice(0, 3).map((subject: any) => (
                          <span key={subject.id} className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-foreground dark:text-muted-foreground text-xs rounded-md">
                            {subject.subject_name}
                          </span>
                        ))
                      ) : (
                        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-muted-foreground dark:text-muted-foreground text-xs rounded-md">
                          No subjects yet
                        </span>
                      )}
                      {subjectCount > 3 && (
                        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-muted-foreground dark:text-muted-foreground text-xs rounded-md">
                          +{subjectCount - 3} more
                        </span>
                      )}
                    </div>

                    {/* Student Count */}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                      <Users className="w-4 h-4" />
                      <span>{studentCount.toLocaleString()} students</span>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-0">
                  {/* Admin Action Buttons */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <Button
                      className={`${colorScheme.button} text-primary-foreground border-0`}
                      size="sm"
                      onClick={() => handleAddSubject(course)}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Subject
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditCourse(course)}
                      className="text-blue-600 hover:text-blue-700 border-blue-200 hover:border-blue-300"
                    >
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteCourse(course.id)}
                      className="text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </Button>
                  </div>

                  {/* Expandable Subjects Section */}
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-foreground">Subjects</h4>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleCourseExpansion(course.id)}
                        className="gap-2"
                      >
                        {expandedCourseId === course.id ? (
                          <>
                            <ChevronDown className="w-4 h-4" />
                            Hide Subjects
                          </>
                        ) : (
                          <>
                            <ChevronRight className="w-4 h-4" />
                            Show Subjects ({subjectCount})
                          </>
                        )}
                      </Button>
                    </div>

                    {expandedCourseId === course.id && (
                      <div className="space-y-2">
                        {loadingSubjects.has(course.id) ? (
                          <div className="flex items-center justify-center py-6">
                            <Loader2 className="w-5 h-5 animate-spin mr-2" />
                            <span className="text-muted-foreground">Loading subjects...</span>
                          </div>
                        ) : courseSubjects[course.id] && courseSubjects[course.id].length > 0 ? (
                          courseSubjects[course.id].map((subject: any) => (
                            <div key={subject.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <h5 className="font-medium">{subject.subject_name}</h5>
                                  {subject.is_bundle && (
                                    <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-md">Bundle</span>
                                  )}
                                  {subject.is_deleted && (
                                    <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-md">Deleted</span>
                                  )}
                                </div>
                                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                                  <span>₹{subject.amount || 0}</span>
                                  {subject.offer_amount && (
                                    <span className="text-green-600">Offer: ₹{subject.offer_amount}</span>
                                  )}
                                  <span>{subject.max_tokens || 100} tokens</span>
                                  <span>{subject.total_mock || 50} tests</span>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleEditSubject(subject)}
                                  className="text-blue-600 hover:text-blue-700 border-blue-200 hover:border-blue-300"
                                >
                                  <Edit2 className="w-3 h-3" />
                                </Button>
                                {!subject.is_deleted && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleSoftDeleteSubject(subject)}
                                    className="text-orange-600 hover:text-orange-700 border-orange-200 hover:border-orange-300"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </Button>
                                )}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-6 text-muted-foreground">
                            <BookOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p>No subjects added yet</p>
                            <p className="text-sm">Click "Add Subject" to get started</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Subject Creation Modal */}
        <Dialog open={isSubjectDialogOpen} onOpenChange={setIsSubjectDialogOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Add New Subject</DialogTitle>
              <DialogDescription>
                Create a new subject for {subjectModalCourse?.course_name || subjectModalCourse?.name}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="subject_name">Subject Name *</Label>
                <Input
                  id="subject_name"
                  placeholder="e.g., Physics, Mathematics"
                  value={subjectFormData.subject_name}
                  onChange={(e) => setSubjectFormData({ ...subjectFormData, subject_name: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amount">Regular Price (₹)</Label>
                  <Input
                    id="amount"
                    type="number"
                    placeholder="299"
                    value={subjectFormData.amount}
                    onChange={(e) => setSubjectFormData({ ...subjectFormData, amount: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="offer_amount">Offer Price (₹)</Label>
                  <Input
                    id="offer_amount"
                    type="number"
                    placeholder="199"
                    value={subjectFormData.offer_amount}
                    onChange={(e) => setSubjectFormData({ ...subjectFormData, offer_amount: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="max_tokens">Max AI Tokens</Label>
                  <Input
                    id="max_tokens"
                    type="number"
                    placeholder="100"
                    value={subjectFormData.max_tokens}
                    onChange={(e) => setSubjectFormData({ ...subjectFormData, max_tokens: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="total_mock">Total Mock Tests</Label>
                  <Input
                    id="total_mock"
                    type="number"
                    placeholder="50"
                    value={subjectFormData.total_mock}
                    onChange={(e) => setSubjectFormData({ ...subjectFormData, total_mock: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_bundle"
                  checked={subjectFormData.is_bundle}
                  onCheckedChange={(checked) => setSubjectFormData({ ...subjectFormData, is_bundle: checked as boolean })}
                />
                <Label htmlFor="is_bundle" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Is Bundle (Multiple subjects package)
                </Label>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => {
                setIsSubjectDialogOpen(false);
                setSubjectModalCourse(null);
                setSubjectFormData({ subject_name: '', amount: '', offer_amount: '', max_tokens: '', total_mock: '', is_bundle: false });
              }}>
                Cancel
              </Button>
              <Button onClick={handleCreateSubject}>Create Subject</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Edit Course Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Edit Course</DialogTitle>
              <DialogDescription>
                Update course information and pricing.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Course Name *</Label>
                <Input
                  id="edit-name"
                  placeholder="Enter course name"
                  value={editFormData.name}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  placeholder="Enter course description"
                  value={editFormData.description}
                  onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-price">Price (₹)</Label>
                  <Input
                    id="edit-price"
                    type="number"
                    placeholder="999"
                    value={editFormData.price}
                    onChange={(e) => setEditFormData({ ...editFormData, price: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-offer-price">Offer Price (₹)</Label>
                  <Input
                    id="edit-offer-price"
                    type="number"
                    placeholder="699"
                    value={editFormData.offerPrice}
                    onChange={(e) => setEditFormData({ ...editFormData, offerPrice: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-max-tokens">Max AI Tokens</Label>
                <Input
                  id="edit-max-tokens"
                  type="number"
                  placeholder="100"
                  value={editFormData.maxTokens}
                  onChange={(e) => setEditFormData({ ...editFormData, maxTokens: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter className="flex justify-between">
              <Button
                variant="destructive"
                onClick={() => handleSoftDeleteCourse(editingCourse?.id)}
                className="mr-auto"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Soft Delete Course
              </Button>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => {
                  setIsEditDialogOpen(false);
                  setEditingCourse(null);
                  setEditFormData({ name: '', description: '', price: '', offerPrice: '', maxTokens: '' });
                }}>
                  Cancel
                </Button>
                <Button onClick={handleUpdateCourse}>Update Course</Button>
              </div>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Edit Subject Dialog */}
        <Dialog open={isEditSubjectDialogOpen} onOpenChange={setIsEditSubjectDialogOpen}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Edit Subject</DialogTitle>
              <DialogDescription>
                Update subject information, pricing, and settings.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="edit-subject-name">Subject Name *</Label>
                <Input
                  id="edit-subject-name"
                  placeholder="Enter subject name"
                  value={editSubjectFormData.subject_name}
                  onChange={(e) => setEditSubjectFormData({ ...editSubjectFormData, subject_name: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-subject-amount">Price (₹)</Label>
                  <Input
                    id="edit-subject-amount"
                    type="number"
                    placeholder="299"
                    value={editSubjectFormData.amount}
                    onChange={(e) => setEditSubjectFormData({ ...editSubjectFormData, amount: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-subject-offer">Offer Price (₹)</Label>
                  <Input
                    id="edit-subject-offer"
                    type="number"
                    placeholder="199"
                    value={editSubjectFormData.offer_amount}
                    onChange={(e) => setEditSubjectFormData({ ...editSubjectFormData, offer_amount: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-subject-tokens">Max AI Tokens</Label>
                  <Input
                    id="edit-subject-tokens"
                    type="number"
                    placeholder="100"
                    value={editSubjectFormData.max_tokens}
                    onChange={(e) => setEditSubjectFormData({ ...editSubjectFormData, max_tokens: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-subject-tests">Total Mock Tests</Label>
                  <Input
                    id="edit-subject-tests"
                    type="number"
                    placeholder="50"
                    value={editSubjectFormData.total_mock}
                    onChange={(e) => setEditSubjectFormData({ ...editSubjectFormData, total_mock: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="edit-is-bundle"
                  checked={editSubjectFormData.is_bundle}
                  onCheckedChange={(checked) => setEditSubjectFormData({ ...editSubjectFormData, is_bundle: checked as boolean })}
                />
                <Label htmlFor="edit-is-bundle" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Is Bundle Package
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="edit-is-deleted"
                  checked={editSubjectFormData.is_deleted}
                  onCheckedChange={(checked) => setEditSubjectFormData({ ...editSubjectFormData, is_deleted: checked as boolean })}
                />
                <Label htmlFor="edit-is-deleted" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Soft Delete (Hide from users)
                </Label>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => {
                setIsEditSubjectDialogOpen(false);
                setEditingSubject(null);
                setEditSubjectFormData({
                  subject_name: '', amount: '', offer_amount: '', max_tokens: '',
                  total_mock: '', is_bundle: false, is_deleted: false
                });
              }}>
                Cancel
              </Button>
              <Button onClick={handleUpdateSubject}>Update Subject</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
