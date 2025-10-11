import { useState, useEffect } from 'react';
import Header from '../Header';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Plus,
  Edit2,
  Trash2,
  Search,
  BookOpen,
  Users,
  DollarSign,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { useAppDispatch, useAppSelector } from '../../store';
import { fetchCourses, createCourse, updateCourse, deleteCourse } from '../../store/slices/adminSlice';

interface ManageCoursesProps {
  user: any;
}

export default function ManageCourses({ user }: ManageCoursesProps) {
  const dispatch = useAppDispatch();
  const { courses, isLoading, error } = useAppSelector((state) => state.admin);

  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingCourse, setEditingCourse] = useState<any>(null);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    subjects: '',
    testCount: '',
    price: '',
    difficulty: 'medium'
  });

  useEffect(() => {
    dispatch(fetchCourses());
  }, [dispatch]);

  // Courses now come from Redux state

  const filteredCourses = courses.filter(course =>
    course.course_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    course.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateCourse = async () => {
    if (!formData.name || !formData.price) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const courseData = {
        course_name: formData.name,
        description: formData.description,
        subjects: formData.subjects,
        test_count: parseInt(formData.testCount) || 0,
        price: parseInt(formData.price),
        difficulty: formData.difficulty
      };

      await dispatch(createCourse(courseData)).unwrap();
      setFormData({ name: '', description: '', subjects: '', testCount: '', price: '', difficulty: 'medium' });
      setIsCreateDialogOpen(false);
      toast.success('Course created successfully!');
    } catch (error) {
      toast.error('Failed to create course');
    }
  };

  const handleEditCourse = (course: any) => {
    setEditingCourse(course);
    setFormData({
      name: course.course_name || course.name,
      description: course.description || '',
      subjects: course.subjects || '',
      testCount: course.test_count?.toString() || '0',
      price: course.price?.toString() || '0',
      difficulty: course.difficulty || 'medium'
    });
  };

  const handleUpdateCourse = async () => {
    if (!formData.name || !formData.price) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const courseData = {
        course_name: formData.name,
        description: formData.description,
        subjects: formData.subjects,
        test_count: parseInt(formData.testCount) || 0,
        price: parseInt(formData.price),
        difficulty: formData.difficulty
      };

      await dispatch(updateCourse({ id: editingCourse.id, ...courseData })).unwrap();
      setEditingCourse(null);
      setFormData({ name: '', description: '', subjects: '', testCount: '', price: '', difficulty: 'medium' });
      toast.success('Course updated successfully!');
    } catch (error) {
      toast.error('Failed to update course');
    }
  };

  const handleDeleteCourse = async (courseId: number) => {
    try {
      await dispatch(deleteCourse(courseId)).unwrap();
      toast.success('Course deleted successfully!');
    } catch (error) {
      toast.error('Failed to delete course');
    }
  };

  const handleToggleStatus = async (courseId: number) => {
    try {
      const course = courses.find(c => c.id === courseId);
      if (course) {
        const updatedCourse = {
          ...course,
          status: course.status === 'active' ? 'inactive' : 'active'
        };
        await dispatch(updateCourse(updatedCourse)).unwrap();
        toast.success('Course status updated!');
      }
    } catch (error) {
      toast.error('Failed to update course status');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading courses...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4">Error Loading Courses</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => dispatch(fetchCourses())}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2">Manage Courses & Subjects</h1>
            <p className="text-xl text-gray-600">Create and manage test courses</p>
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
                <DialogTitle>Create New Course</DialogTitle>
                <DialogDescription>Add a new course or test series</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Course Name *</Label>
                    <Input
                      id="name"
                      placeholder="e.g., NEET Physics"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="subjects">Subject</Label>
                    <Input
                      id="subjects"
                      placeholder="e.g., Physics"
                      value={formData.subjects}
                      onChange={(e) => setFormData({ ...formData, subjects: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Course description..."
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="testCount">Number of Tests</Label>
                    <Input
                      id="testCount"
                      type="number"
                      placeholder="150"
                      value={formData.testCount}
                      onChange={(e) => setFormData({ ...formData, testCount: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="price">Price (₹) *</Label>
                    <Input
                      id="price"
                      type="number"
                      placeholder="499"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="difficulty">Difficulty</Label>
                    <Select
                      value={formData.difficulty}
                      onValueChange={(value) => setFormData({ ...formData, difficulty: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="easy">Easy</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="hard">Hard</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
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

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Courses</p>
                  <p className="text-3xl">{courses.length}</p>
                </div>
                <BookOpen className="w-10 h-10 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Students</p>
                  <p className="text-3xl">{courses.reduce((sum, c) => sum + (c.students || 0), 0).toLocaleString()}</p>
                </div>
                <Users className="w-10 h-10 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Tests</p>
                  <p className="text-3xl">{courses.reduce((sum, c) => sum + (c.test_count || 0), 0)}</p>
                </div>
                <DollarSign className="w-10 h-10 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search courses..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Courses Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Courses</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Course Name</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Tests</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Students</TableHead>
                  <TableHead>Difficulty</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCourses.map((course) => (
                  <TableRow key={course.id}>
                    <TableCell>{course.course_name || course.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{course.subjects || course.subject || 'General'}</Badge>
                    </TableCell>
                    <TableCell>{course.test_count || course.tests || 0}</TableCell>
                    <TableCell>₹{course.price || 0}</TableCell>
                    <TableCell>{(course.students || 0).toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge variant={
                        course.difficulty === 'easy' ? 'default' :
                        course.difficulty === 'medium' ? 'secondary' :
                        'destructive'
                      }>
                        {course.difficulty || 'medium'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={course.status === 'active' ? 'default' : 'secondary'}
                        className="cursor-pointer"
                        onClick={() => handleToggleStatus(course.id)}
                      >
                        {course.status || 'active'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleEditCourse(course)}
                            >
                              <Edit2 className="w-4 h-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>Edit Course</DialogTitle>
                              <DialogDescription>Update course details</DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4">
                              <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                  <Label htmlFor="edit-name">Course Name</Label>
                                  <Input
                                    id="edit-name"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label htmlFor="edit-subjects">Subject</Label>
                                  <Input
                                    id="edit-subjects"
                                    value={formData.subjects}
                                    onChange={(e) => setFormData({ ...formData, subjects: e.target.value })}
                                  />
                                </div>
                              </div>
                              <div className="grid grid-cols-3 gap-4">
                                <div className="space-y-2">
                                  <Label htmlFor="edit-testCount">Number of Tests</Label>
                                  <Input
                                    id="edit-testCount"
                                    type="number"
                                    value={formData.testCount}
                                    onChange={(e) => setFormData({ ...formData, testCount: e.target.value })}
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label htmlFor="edit-price">Price (₹)</Label>
                                  <Input
                                    id="edit-price"
                                    type="number"
                                    value={formData.price}
                                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label htmlFor="edit-difficulty">Difficulty</Label>
                                  <Select
                                    value={formData.difficulty}
                                    onValueChange={(value) => setFormData({ ...formData, difficulty: value })}
                                  >
                                    <SelectTrigger>
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="easy">Easy</SelectItem>
                                      <SelectItem value="medium">Medium</SelectItem>
                                      <SelectItem value="hard">Hard</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                              </div>
                            </div>
                            <DialogFooter>
                              <Button variant="outline" onClick={() => setEditingCourse(null)}>
                                Cancel
                              </Button>
                              <Button onClick={handleUpdateCourse}>Update Course</Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleDeleteCourse(course.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
