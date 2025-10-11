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

interface MockTestPurchaseProps {
  user: any;
}

export default function MockTestPurchase({ user }: MockTestPurchaseProps) {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { currentCart, isLoading, error } = useAppSelector((state) => state.purchase);

  const [paymentMethod, setPaymentMethod] = useState('card');
  const [cardNumber, setCardNumber] = useState('');
  const [cardName, setCardName] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [upiId, setUpiId] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Check if cart is empty and redirect
  useEffect(() => {
    if (!currentCart || !currentCart.items || currentCart.items.length === 0) {
      toast.error('Your cart is empty');
      navigate('/courses');
    }
  }, [currentCart, navigate]);

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

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (paymentMethod === 'card') {
      if (!cardNumber || !cardName || !expiryDate || !cvv) {
        toast.error('Please fill in all card details');
        return;
      }
    } else if (paymentMethod === 'upi') {
      if (!upiId) {
        toast.error('Please enter UPI ID');
        return;
      }
    }

    setIsProcessing(true);
    
    // Process payment through Redux
    try {
      // For demo purposes, we'll purchase each item separately
      for (const item of currentCart.items) {
        const purchaseData = {
          courseId: currentCart.courseId || '',
          subjectId: item.type === 'subject' ? item.id : undefined,
          paymentMethod
        };

        await dispatch(processPurchase(purchaseData)).unwrap();
      }

      dispatch(clearCart());

      setIsProcessing(false);
      toast.success('Payment successful! Access granted to selected tests.');
      navigate('/dashboard');
    } catch (error) {
      setIsProcessing(false);
      const errorMessage = error instanceof Error ? error.message : 'Payment failed. Please try again.';
      toast.error(errorMessage);
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
                        <span className="text-gray-500">({item.tests || 100} tests)</span>
                      </span>
                      <span>₹{item.price}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Payment Method */}
            <Card>
              <CardHeader>
                <CardTitle>Payment Method</CardTitle>
              </CardHeader>
              <CardContent>
                <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod}>
                  <div className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="card" id="card" />
                    <Label htmlFor="card" className="flex items-center gap-2 cursor-pointer flex-1">
                      <CreditCard className="w-5 h-5" />
                      <span>Credit / Debit Card</span>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="upi" id="upi" />
                    <Label htmlFor="upi" className="flex items-center gap-2 cursor-pointer flex-1">
                      <Smartphone className="w-5 h-5" />
                      <span>UPI</span>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="netbanking" id="netbanking" />
                    <Label htmlFor="netbanking" className="flex items-center gap-2 cursor-pointer flex-1">
                      <Building2 className="w-5 h-5" />
                      <span>Net Banking</span>
                    </Label>
                  </div>
                </RadioGroup>

                <form onSubmit={handlePayment} className="mt-6 space-y-4">
                  {paymentMethod === 'card' && (
                    <>
                      <div className="space-y-2">
                        <Label htmlFor="cardNumber">Card Number</Label>
                        <Input
                          id="cardNumber"
                          placeholder="1234 5678 9012 3456"
                          value={cardNumber}
                          onChange={(e) => setCardNumber(e.target.value)}
                          maxLength={19}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="cardName">Cardholder Name</Label>
                        <Input
                          id="cardName"
                          placeholder="John Doe"
                          value={cardName}
                          onChange={(e) => setCardName(e.target.value)}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="expiry">Expiry Date</Label>
                          <Input
                            id="expiry"
                            placeholder="MM/YY"
                            value={expiryDate}
                            onChange={(e) => setExpiryDate(e.target.value)}
                            maxLength={5}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="cvv">CVV</Label>
                          <Input
                            id="cvv"
                            type="password"
                            placeholder="123"
                            value={cvv}
                            onChange={(e) => setCvv(e.target.value)}
                            maxLength={3}
                          />
                        </div>
                      </div>
                    </>
                  )}

                  {paymentMethod === 'upi' && (
                    <div className="space-y-2">
                      <Label htmlFor="upiId">UPI ID</Label>
                      <Input
                        id="upiId"
                        placeholder="yourname@upi"
                        value={upiId}
                        onChange={(e) => setUpiId(e.target.value)}
                      />
                    </div>
                  )}

                  {paymentMethod === 'netbanking' && (
                    <div className="p-4 bg-blue-50 rounded-lg text-sm">
                      <p>You will be redirected to your bank's secure payment gateway</p>
                    </div>
                  )}

                  <Button 
                    type="submit" 
                    size="lg" 
                    className="w-full"
                    disabled={isProcessing}
                  >
                    <Lock className="w-4 h-4 mr-2" />
                    {isProcessing ? 'Processing...' : `Pay ₹${total}`}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Security Badge */}
            <div className="flex items-center justify-center gap-4 text-sm text-gray-600">
              <Shield className="w-5 h-5" />
              <span>Your payment information is secure and encrypted</span>
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
