import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
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
  BookOpen,
  DollarSign,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { useAppDispatch, useAppSelector } from '../../store';
import { 
  fetchSubjects, 
  createSubject, 
  updateSubject, 
  deleteSubject 
} from '../../store/slices/adminSlice';

interface ManageSubjectsProps {
  courseId: number;
  courseName: string;
}

export default function ManageSubjects({ courseId, courseName }: ManageSubjectsProps) {
  const dispatch = useAppDispatch();
  const { subjects, isLoading } = useAppSelector((state) => state.admin);

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<any>(null);

  const [formData, setFormData] = useState({
    subject_name: '',
    amount: '',
    offer_amount: '',
    max_tokens: ''
  });

  useEffect(() => {
    if (courseId) {
      dispatch(fetchSubjects(courseId));
    }
  }, [dispatch, courseId]);

  const resetForm = () => {
    setFormData({
      subject_name: '',
      amount: '',
      offer_amount: '',
      max_tokens: ''
    });
  };

  const handleCreateSubject = async () => {
    if (!formData.subject_name.trim()) {
      toast.error('Subject name is required');
      return;
    }

    try {
      const subjectData = {
        course_id: courseId,
        subject_name: formData.subject_name.trim(),
        amount: parseFloat(formData.amount) || 0,
        offer_amount: parseFloat(formData.offer_amount) || 0,
        max_tokens: parseInt(formData.max_tokens) || 100
      };

      await dispatch(createSubject(subjectData)).unwrap();
      resetForm();
      setIsCreateDialogOpen(false);
      toast.success('Subject created successfully!');
    } catch (error) {
      toast.error('Failed to create subject');
    }
  };

  const handleEditSubject = (subject: any) => {
    setEditingSubject(subject);
    setFormData({
      subject_name: subject.subject_name || '',
      amount: subject.amount?.toString() || '0',
      offer_amount: subject.offer_amount?.toString() || '0',
      max_tokens: subject.max_tokens?.toString() || '100'
    });
  };

  const handleUpdateSubject = async () => {
    if (!formData.subject_name.trim()) {
      toast.error('Subject name is required');
      return;
    }

    try {
      const subjectData = {
        subject_name: formData.subject_name.trim(),
        amount: parseFloat(formData.amount) || 0,
        offer_amount: parseFloat(formData.offer_amount) || 0,
        max_tokens: parseInt(formData.max_tokens) || 100
      };

      await dispatch(updateSubject({ id: editingSubject.id, data: subjectData })).unwrap();
      setEditingSubject(null);
      resetForm();
      toast.success('Subject updated successfully!');
    } catch (error) {
      toast.error('Failed to update subject');
    }
  };

  const handleDeleteSubject = async (subjectId: number) => {
    if (!confirm('Are you sure you want to delete this subject?')) {
      return;
    }

    try {
      await dispatch(deleteSubject(subjectId)).unwrap();
      toast.success('Subject deleted successfully!');
    } catch (error) {
      toast.error('Failed to delete subject');
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              Subjects for {courseName}
            </CardTitle>
            <p className="text-sm text-gray-600 mt-1">
              Manage subjects and their pricing for this course
            </p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="w-4 h-4" />
                Add Subject
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>Add New Subject</DialogTitle>
                <DialogDescription>
                  Create a new subject for {courseName}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="subject_name">Subject Name *</Label>
                  <Input
                    id="subject_name"
                    placeholder="e.g., Physics, Mathematics"
                    value={formData.subject_name}
                    onChange={(e) => setFormData({ ...formData, subject_name: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="amount">Regular Price (₹)</Label>
                    <Input
                      id="amount"
                      type="number"
                      placeholder="299"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="offer_amount">Offer Price (₹)</Label>
                    <Input
                      id="offer_amount"
                      type="number"
                      placeholder="199"
                      value={formData.offer_amount}
                      onChange={(e) => setFormData({ ...formData, offer_amount: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="max_tokens">Max AI Tokens</Label>
                    <Input
                      id="max_tokens"
                      type="number"
                      placeholder="100"
                      value={formData.max_tokens}
                      onChange={(e) => setFormData({ ...formData, max_tokens: e.target.value })}
                    />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => {
                  setIsCreateDialogOpen(false);
                  resetForm();
                }}>
                  Cancel
                </Button>
                <Button onClick={handleCreateSubject}>Create Subject</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span className="ml-2">Loading subjects...</span>
          </div>
        ) : subjects.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No subjects found for this course</p>
            <p className="text-sm">Add your first subject to get started</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Subject Name</TableHead>
                <TableHead>Regular Price</TableHead>
                <TableHead>Offer Price</TableHead>
                <TableHead>AI Tokens</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {subjects.map((subject) => (
                <TableRow key={subject.id}>
                  <TableCell className="font-medium">{subject.subject_name}</TableCell>
                  <TableCell>₹{subject.amount || 0}</TableCell>
                  <TableCell>
                    {subject.offer_amount ? (
                      <span className="text-green-600 font-medium">₹{subject.offer_amount}</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {subject.max_tokens === 0 ? (
                      <Badge variant="secondary">Unlimited</Badge>
                    ) : (
                      <span>{subject.max_tokens || 100}</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleEditSubject(subject)}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[500px]">
                          <DialogHeader>
                            <DialogTitle>Edit Subject</DialogTitle>
                            <DialogDescription>
                              Update subject details and pricing
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="space-y-2">
                              <Label htmlFor="edit-subject_name">Subject Name *</Label>
                              <Input
                                id="edit-subject_name"
                                value={formData.subject_name}
                                onChange={(e) => setFormData({ ...formData, subject_name: e.target.value })}
                              />
                            </div>
                            <div className="grid grid-cols-3 gap-4">
                              <div className="space-y-2">
                                <Label htmlFor="edit-amount">Regular Price (₹)</Label>
                                <Input
                                  id="edit-amount"
                                  type="number"
                                  value={formData.amount}
                                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                />
                              </div>
                              <div className="space-y-2">
                                <Label htmlFor="edit-offer_amount">Offer Price (₹)</Label>
                                <Input
                                  id="edit-offer_amount"
                                  type="number"
                                  value={formData.offer_amount}
                                  onChange={(e) => setFormData({ ...formData, offer_amount: e.target.value })}
                                />
                              </div>
                              <div className="space-y-2">
                                <Label htmlFor="edit-max_tokens">Max AI Tokens</Label>
                                <Input
                                  id="edit-max_tokens"
                                  type="number"
                                  value={formData.max_tokens}
                                  onChange={(e) => setFormData({ ...formData, max_tokens: e.target.value })}
                                />
                              </div>
                            </div>
                          </div>
                          <DialogFooter>
                            <Button variant="outline" onClick={() => {
                              setEditingSubject(null);
                              resetForm();
                            }}>
                              Cancel
                            </Button>
                            <Button onClick={handleUpdateSubject}>Update Subject</Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleDeleteSubject(subject.id)}
                      >
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
