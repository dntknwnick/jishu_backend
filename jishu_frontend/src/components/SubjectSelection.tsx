import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Header from './Header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { ArrowLeft, ShoppingCart, Zap, Clock, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchSubjectsByCourse, fetchBundlesByCourse, toggleSubjectSelection, clearSelectedSubjects } from '../store/slices/subjectsSlice';
import { fetchCourseById } from '../store/slices/coursesSlice';
import { setCart } from '../store/slices/purchaseSlice';

interface SubjectSelectionProps {
  user: any;
}

export default function SubjectSelection({ user }: SubjectSelectionProps) {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  const { subjects, bundles, selectedSubjects, isLoading, error } = useAppSelector((state) => state.subjects);
  const { selectedCourse } = useAppSelector((state) => state.courses);

  useEffect(() => {
    if (courseId) {
      const courseIdNum = parseInt(courseId);
      dispatch(fetchCourseById(courseIdNum));
      dispatch(fetchSubjectsByCourse(courseIdNum));
      dispatch(fetchBundlesByCourse(courseIdNum));
      dispatch(clearSelectedSubjects());
    }
  }, [courseId, dispatch]);

  // Get icon for subject
  const getSubjectIcon = (subjectName: string) => {
    const name = subjectName.toLowerCase();
    if (name.includes('physics')) return '⚛️';
    if (name.includes('chemistry')) return '🧪';
    if (name.includes('mathematics') || name.includes('math')) return '📐';
    if (name.includes('biology')) return '🧬';
    return '📚';
  };

  // Get price for subject (mock pricing for now)
  const getSubjectPrice = (subjectName: string) => {
    const name = subjectName.toLowerCase();
    if (name.includes('advanced')) return 599;
    if (name.includes('neet')) return 499;
    return 399;
  };

  const course = selectedCourse;

  // Get the first bundle (there should only be one per course)
  const bundle = bundles && bundles.length > 0 ? bundles[0] : null;

  // Fallback to calculated bundle if no bundle exists in backend
  const bundlePrice = bundle ? (bundle.amount || 0) : subjects.reduce((sum, s) => sum + getSubjectPrice(s.subject_name), 0);
  const bundleFinalPrice = bundle ? (bundle.offer_amount || bundle.amount || 0) : bundlePrice - Math.round(bundlePrice * 0.3);
  const bundleDiscount = bundlePrice - bundleFinalPrice;

  const toggleSubject = (subjectId: number) => {
    dispatch(toggleSubjectSelection(subjectId));
  };

  const handlePurchase = () => {
    if (selectedSubjects.length === 0) {
      toast.error('Please select at least one subject');
      return;
    }

    const selectedItems = subjects
      .filter(s => selectedSubjects.includes(s.id))
      .map(s => ({
        id: s.id,
        name: s.subject_name,
        price: getSubjectPrice(s.subject_name),
        icon: getSubjectIcon(s.subject_name),
        tests: s.total_mock || 50 // Dynamic test count from backend
      }));

    dispatch(setCart({
      items: selectedItems,
      courseId: courseId || null,
      courseName: course?.course_name || '',
      isBundle: false,
      bundleDiscount: 0
    }));

    navigate('/purchase');
  };

  const handleBundlePurchase = () => {
    if (bundle) {
      // Use actual bundle from backend
      const bundleItem = {
        id: bundle.id,
        name: bundle.subject_name,
        price: bundleFinalPrice,
        icon: '📦',
        tests: bundle.total_mock || 0,
        type: 'bundle'
      };

      dispatch(setCart({
        items: [bundleItem],
        courseId: courseId || null,
        courseName: course?.course_name || '',
        isBundle: true,
        bundleDiscount
      }));
    } else {
      // Fallback to all subjects (legacy behavior)
      const allItems = subjects.map(s => ({
        id: s.id,
        name: s.subject_name,
        price: getSubjectPrice(s.subject_name),
        icon: getSubjectIcon(s.subject_name),
        tests: s.total_mock || 50,
        type: 'subject'
      }));

      dispatch(setCart({
        items: allItems,
        courseId: courseId || null,
        courseName: course?.course_name || '',
        isBundle: true,
        bundleDiscount
      }));
    }

    navigate('/purchase');
  };

  const totalPrice = subjects
    .filter(s => selectedSubjects.includes(s.id))
    .reduce((sum, s) => sum + getSubjectPrice(s.subject_name), 0);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading subjects...</span>
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
            <h2 className="text-2xl mb-4">Error Loading Subjects</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => courseId && dispatch(fetchSubjectsByCourse(parseInt(courseId)))}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!course || subjects.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4">No Subjects Found</h2>
            <p className="text-gray-600 mb-4">No subjects available for this course.</p>
            <Link to="/courses">
              <Button>Back to Courses</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 mb-6">
          <Link to="/courses">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Courses
            </Button>
          </Link>
        </div>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl mb-2">Select Subjects for {course.course_name}</h1>
          <p className="text-xl text-gray-600">Choose individual subjects or get the complete bundle</p>
        </div>

        {/* Main Layout: Left Content + Right Cart Summary */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Side - All Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Complete Bundle Section */}
            {(bundle || subjects.length > 0) && (
              <div>
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <Zap className="w-6 h-6 text-purple-600" />
                  Complete Bundle Package
                </h2>
                <Card className="border-2 border-purple-500 bg-gradient-to-br from-purple-50 to-pink-50">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className="bg-purple-600">Best Value</Badge>
                        </div>
                        <CardTitle className="text-2xl">Complete Bundle</CardTitle>
                        <CardDescription>All subjects included with 30% discount</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {subjects.map((subject) => (
                      <Badge key={subject.id} variant="secondary" className="text-sm">
                        {getSubjectIcon(subject.subject_name)} {subject.subject_name}
                      </Badge>
                    ))}
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-gray-500 line-through">₹{bundlePrice}</div>
                    <div className="text-3xl text-purple-600">₹{bundleFinalPrice}</div>
                    <Badge variant="destructive">Save ₹{bundleDiscount}</Badge>
                  </div>

                  <ul className="space-y-2">
                    <li className="flex items-center gap-2 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span>Access to all {bundle ? bundle.total_mock : subjects.reduce((sum, s) => sum + (s.total_mock || 50), 0)} mock tests</span>
                    </li>
                    <li className="flex items-center gap-2 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span>Detailed performance analytics</span>
                    </li>
                    <li className="flex items-center gap-2 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span>1 year validity</span>
                    </li>
                    <li className="flex items-center gap-2 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <span>AI chatbot support</span>
                    </li>
                  </ul>

                  <Button
                    size="lg"
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600"
                    onClick={handleBundlePurchase}
                  >
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    Purchase Bundle
                  </Button>
                </CardContent>
              </Card>
              </div>
            )}

            {/* Individual Subjects Section */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold mb-4">Or select individual subjects</h2>
              {subjects.map((subject) => {
                const price = getSubjectPrice(subject.subject_name);
                const icon = getSubjectIcon(subject.subject_name);

                return (
                  <Card
                    key={subject.id}
                    className={`cursor-pointer transition-all ${
                      selectedSubjects.includes(subject.id)
                        ? 'border-2 border-blue-500 shadow-lg'
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => toggleSubject(subject.id)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <Checkbox
                          checked={selectedSubjects.includes(subject.id)}
                          onCheckedChange={() => toggleSubject(subject.id)}
                          onClick={(e) => e.stopPropagation()}
                        />
                        <div className="text-4xl">{icon}</div>
                        <div className="flex-1">
                          <h4 className="text-xl mb-1">{subject.subject_name}</h4>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <FileText className="w-4 h-4" />
                              {subject.total_mock || 50}+ tests
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              1 year access
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl">₹{price}</div>
                          <div className="text-sm text-gray-500">per subject</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Right Side - Cart Summary */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Cart Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {selectedSubjects.length === 0 ? (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No subjects selected
                  </p>
                ) : (
                  <>
                    <div className="space-y-2">
                      {subjects
                        .filter((s: any) => selectedSubjects.includes(s.id))
                        .map((subject: any) => (
                          <div key={subject.id} className="flex justify-between text-sm">
                            <span>{subject.subject_name}</span>
                            <span>₹{getSubjectPrice(subject.subject_name)}</span>
                          </div>
                        ))
                      }
                    </div>
                    <div className="border-t pt-4">
                      <div className="flex justify-between mb-4">
                        <span className="font-semibold">Total</span>
                        <span className="text-2xl font-bold">₹{totalPrice}</span>
                      </div>
                      <Button
                        size="lg"
                        className="w-full"
                        onClick={handlePurchase}
                      >
                        <ShoppingCart className="w-4 h-4 mr-2" />
                        Proceed to Checkout
                      </Button>
                    </div>
                  </>
                )}

                <div className="border-t pt-4 space-y-2 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <span>Secure payment</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <span>Instant access</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <span>Money-back guarantee</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
