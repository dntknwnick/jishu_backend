import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Header from './Header';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import {
  CreditCard,
  Smartphone,
  Building2,
  CheckCircle2,
  Shield,
  Lock,
  ArrowLeft,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store';
import { processPurchase, clearCart } from '../store/slices/purchaseSlice';
import api from '../services/api';

interface MockTestPurchaseProps {
  user: any;
}

export default function MockTestPurchase({ user }: MockTestPurchaseProps) {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { currentCart, isLoading, error } = useAppSelector((state) => state.purchase);

  // Simplified for local development - no payment gateway needed
  const [isProcessing, setIsProcessing] = useState(false);
  const [purchaseCompleted, setPurchaseCompleted] = useState(false);

  // Check if cart is empty and redirect (but not if purchase was just completed)
  useEffect(() => {
    if (!purchaseCompleted && (!currentCart || !currentCart.items || currentCart.items.length === 0)) {
      toast.error('Your cart is empty');
      navigate('/courses');
    }
  }, [currentCart, navigate, purchaseCompleted]);

  if (!currentCart || !currentCart.items || currentCart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl mb-4">Cart is Empty</h2>
            <p className="text-gray-600 mb-4">Please add items to your cart before proceeding to payment.</p>
            <Button onClick={() => navigate('/courses')}>
              Browse Courses
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const subtotal = currentCart.items.reduce((sum, item) => sum + item.price, 0);
  const discount = currentCart.bundleDiscount || 0;
  const tax = Math.round((subtotal - discount) * 0.18);
  const total = subtotal - discount + tax;

  const handlePurchaseConfirmation = async () => {
    setIsProcessing(true);

    try {
      // Debug: Log current cart
      console.log('Current cart:', currentCart);

      // Determine purchase type based on cart items
      let purchaseType: 'single_subject' | 'multiple_subjects' | 'full_bundle';
      let subjectIds: number[] = [];

      // Check if it's a bundle purchase
      if (currentCart.isBundle || currentCart.items.some(item => item.type === 'bundle')) {
        purchaseType = 'full_bundle';
        // For bundle, get all subject IDs from the bundle or all items
        subjectIds = currentCart.items
          .filter(item => item.type === 'subject' || !item.type) // Include items without type (legacy)
          .map(item => item.id);
      } else if (currentCart.items.length === 1) {
        purchaseType = 'single_subject';
        subjectIds = [currentCart.items[0].id];
      } else if (currentCart.items.length === 2) {
        purchaseType = 'multiple_subjects';
        subjectIds = currentCart.items.map(item => item.id);
      } else {
        // Fallback to full bundle for more than 2 items
        purchaseType = 'full_bundle';
        subjectIds = currentCart.items.map(item => item.id);
      }

      console.log('Purchase type:', purchaseType);
      console.log('Subject IDs:', subjectIds);

      // Create purchase using new API with correct field names
      const purchaseData: any = {
        course_id: parseInt(currentCart.courseId || '0'),
        purchase_type: purchaseType,
        cost: total
      };

      // Add subject fields based on purchase type
      if (purchaseType === 'single_subject') {
        purchaseData.subject_id = subjectIds[0]; // Single subject ID
      } else {
        purchaseData.subject_ids = subjectIds; // Multiple subject IDs
      }

      // Validate course ID
      if (!purchaseData.course_id || purchaseData.course_id === 0) {
        throw new Error('Invalid course ID. Please try selecting the course again.');
      }

      console.log('Final purchase data:', purchaseData);

      const response = await api.purchase.createPurchase(purchaseData);

      // Mark purchase as completed before clearing cart to prevent redirect
      setPurchaseCompleted(true);

      dispatch(clearCart());

      toast.success(
        `Purchase completed! ${response.data.test_cards_created} test cards created. You now have access to ${response.data.total_test_cards} total test cards.`
      );

      // Small delay to ensure toast is visible before navigation
      setTimeout(() => {
        // Redirect to test card dashboard
        navigate('/results', {
          state: {
            purchaseSuccess: true,
            purchaseData: response.data,
            message: `Course access granted! ${response.data.test_cards_created} test cards are now available.`
          }
        });
      }, 1000); // 1 second delay to show success message
    } catch (error) {
      console.error('Purchase failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to complete purchase. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  // This check is now handled above with currentCart

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-2 mb-6">
          <Link to={`/subjects/${currentCart.courseId}`}>
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
        </div>

        <h1 className="text-4xl mb-8">Checkout</h1>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Payment Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Order Summary Card */}
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg">{currentCart.courseName}</h3>
                    {currentCart.isBundle && (
                      <Badge className="mt-1">Complete Bundle</Badge>
                    )}
                  </div>
                </div>
                <div className="space-y-2">
                  {currentCart.items.map((item, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2">
                        <span>{item.icon}</span>
                        <span>{item.name}</span>
                        <span className="text-gray-500">({item.tests || 50} tests)</span>
                      </span>
                      <span>₹{item.price}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Local Development - Instant Access */}
            <Card>
              <CardHeader>
                <CardTitle>Local Development Mode</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">Instant Access Available</span>
                  </div>
                  <p className="text-sm text-green-700">
                    In local development mode, you get instant access to all purchased content without payment processing.
                  </p>
                </div>

                <div className="mt-6">
                  <Button
                    onClick={handlePurchaseConfirmation}
                    size="lg"
                    className="w-full bg-green-600 hover:bg-green-700"
                    disabled={isProcessing}
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4 mr-2" />
                        Get Instant Access - ₹{total}
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Development Mode Info */}
            <div className="flex items-center justify-center gap-4 text-sm text-gray-600">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <span>Local development mode - instant access without payment processing</span>
            </div>
          </div>

          {/* Order Summary Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Price Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span>₹{subtotal}</span>
                  </div>
                  {discount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount</span>
                      <span>-₹{discount}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>GST (18%)</span>
                    <span>₹{tax}</span>
                  </div>
                </div>

                <Separator />

                <div className="flex justify-between text-xl">
                  <span>Total</span>
                  <span>₹{total}</span>
                </div>

                <div className="pt-4 space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" />
                    <span>Instant access after payment</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" />
                    <span>1 year validity</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" />
                    <span>Detailed analytics included</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" />
                    <span>AI chatbot support</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5" />
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
