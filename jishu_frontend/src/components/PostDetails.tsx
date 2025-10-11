import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Header from './Header';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Separator } from './ui/separator';
import { 
  Heart, 
  MessageCircle, 
  Share2,
  ArrowLeft,
  Send,
  ThumbsUp,
  Clock
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface PostDetailsProps {
  user: any;
}

export default function PostDetails({ user }: PostDetailsProps) {
  const { postId } = useParams();
  const [isLiked, setIsLiked] = useState(false);
  const [likes, setLikes] = useState(234);
  const [commentText, setCommentText] = useState('');
  const [comments, setComments] = useState([
    {
      id: 1,
      author: {
        name: 'Aditya Verma',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aditya'
      },
      content: 'This is really helpful! I\'ve been struggling with this topic. Thanks for sharing!',
      timeAgo: '1 hour ago',
      likes: 12,
      isLiked: false
    },
    {
      id: 2,
      author: {
        name: 'Neha Kapoor',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Neha'
      },
      content: 'Could you share more details about the second strategy? I\'d love to try it.',
      timeAgo: '2 hours ago',
      likes: 8,
      isLiked: false
    },
    {
      id: 3,
      author: {
        name: 'Karan Shah',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Karan'
      },
      content: 'Awesome post! This motivated me to study harder. Keep posting such content!',
      timeAgo: '3 hours ago',
      likes: 15,
      isLiked: true
    }
  ]);

  const post = {
    id: postId,
    author: {
      name: 'Priya Sharma',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Priya',
      role: 'NEET Aspirant',
      followers: '1.2K'
    },
    title: 'How I Improved My Biology Score by 30%',
    content: `Hello everyone! 👋

I wanted to share my journey of improving my biology scores from 60% to 90% in just 3 months. If you're struggling with biology, I hope these tips help you too!

**1. Master the NCERT First**
I know everyone says this, but it's true. I read each chapter 3 times - first for understanding, second for memorization, and third for revision. Make notes of diagrams and important points.

**2. Make Visual Mnemonics**
Biology has so many terms to remember! I created visual mnemonics for complex processes like Krebs cycle, photosynthesis, etc. Draw flowcharts and stick them on your wall.

**3. Practice Previous Year Questions**
I solved all NEET biology questions from the past 10 years. This helped me understand the pattern and frequently asked topics. Focus on Human Physiology, Genetics, and Ecology.

**4. Use Quality Mock Tests**
Taking regular mock tests on Jishu App really helped me identify my weak areas. The detailed analytics showed me exactly where I needed to improve.

**5. Stay Consistent**
I studied biology for 2-3 hours every day without fail. Consistency is more important than studying for long hours occasionally.

Remember, improvement takes time. Don't get discouraged if you don't see results immediately. Keep working hard, and you'll definitely succeed!

Feel free to ask any questions in the comments. Happy studying! 📚`,
    image: 'https://images.unsplash.com/photo-1566827886072-417be1953f36?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsZWFybmluZyUyMGJvb2slMjBkZXNrfGVufDF8fHx8MTc2MDAyOTI3Nnww&ixlib=rb-4.1.0&q=80&w=1080',
    tags: ['Biology', 'Study Tips', 'NEET'],
    timeAgo: '2 hours ago',
    views: 1240
  };

  const togglePostLike = () => {
    setIsLiked(!isLiked);
    setLikes(isLiked ? likes - 1 : likes + 1);
  };

  const toggleCommentLike = (commentId: number) => {
    setComments(comments.map(comment => {
      if (comment.id === commentId) {
        return {
          ...comment,
          isLiked: !comment.isLiked,
          likes: comment.isLiked ? comment.likes - 1 : comment.likes + 1
        };
      }
      return comment;
    }));
  };

  const handleAddComment = () => {
    if (!commentText.trim()) {
      toast.error('Please write a comment');
      return;
    }

    const newComment = {
      id: comments.length + 1,
      author: {
        name: user.name,
        avatar: user.avatar
      },
      content: commentText,
      timeAgo: 'Just now',
      likes: 0,
      isLiked: false
    };

    setComments([newComment, ...comments]);
    setCommentText('');
    toast.success('Comment added!');
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Link copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link to="/community">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Community
            </Button>
          </Link>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Card>
              {post.image && (
                <ImageWithFallback
                  src={post.image}
                  alt={post.title}
                  className="w-full h-96 object-cover"
                />
              )}
              <CardHeader>
                {/* Author Info */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src={post.author.avatar} alt={post.author.name} />
                      <AvatarFallback>{post.author.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <h4>{post.author.name}</h4>
                      <p className="text-sm text-gray-600">{post.author.role} • {post.author.followers} followers</p>
                    </div>
                  </div>
                  <Button>Follow</Button>
                </div>

                {/* Title and Meta */}
                <h1 className="text-4xl mb-4">{post.title}</h1>
                <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {post.timeAgo}
                  </span>
                  <span>•</span>
                  <span>{post.views} views</span>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {post.tags.map((tag, idx) => (
                    <Badge key={idx} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-4">
                  <Button
                    variant={isLiked ? 'default' : 'outline'}
                    onClick={togglePostLike}
                    className="gap-2"
                  >
                    <Heart className={isLiked ? 'fill-current' : ''} />
                    {likes}
                  </Button>
                  <Button variant="outline" className="gap-2">
                    <MessageCircle />
                    {comments.length}
                  </Button>
                  <Button variant="outline" onClick={handleShare} className="gap-2">
                    <Share2 />
                    Share
                  </Button>
                </div>
              </CardHeader>

              <Separator />

              {/* Post Content */}
              <CardContent className="p-8">
                <div className="prose max-w-none">
                  {post.content.split('\n').map((paragraph, idx) => (
                    <p key={idx} className="mb-4 text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </CardContent>

              <Separator />

              {/* Comments Section */}
              <CardContent className="p-8 space-y-6">
                <h3 className="text-2xl">Comments ({comments.length})</h3>

                {/* Add Comment */}
                <div className="flex gap-3">
                  <Avatar>
                    <AvatarImage src={user.avatar} alt={user.name} />
                    <AvatarFallback>{user.name?.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-2">
                    <Textarea
                      placeholder="Write a comment..."
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      rows={3}
                    />
                    <Button onClick={handleAddComment} className="gap-2">
                      <Send className="w-4 h-4" />
                      Post Comment
                    </Button>
                  </div>
                </div>

                <Separator />

                {/* Comments List */}
                <div className="space-y-6">
                  {comments.map((comment) => (
                    <div key={comment.id} className="flex gap-3">
                      <Avatar>
                        <AvatarImage src={comment.author.avatar} alt={comment.author.name} />
                        <AvatarFallback>{comment.author.name.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4>{comment.author.name}</h4>
                            <span className="text-xs text-gray-500">{comment.timeAgo}</span>
                          </div>
                          <p className="text-gray-700">{comment.content}</p>
                        </div>
                        <div className="flex items-center gap-4 mt-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleCommentLike(comment.id)}
                            className="gap-2"
                          >
                            <ThumbsUp className={`w-4 h-4 ${comment.isLiked ? 'fill-blue-500 text-blue-500' : ''}`} />
                            <span>{comment.likes}</span>
                          </Button>
                          <Button variant="ghost" size="sm">
                            Reply
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Author Card */}
            <Card>
              <CardHeader>
                <h3 className="text-lg">About the Author</h3>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <Avatar className="w-24 h-24 mx-auto">
                  <AvatarImage src={post.author.avatar} alt={post.author.name} />
                  <AvatarFallback>{post.author.name.charAt(0)}</AvatarFallback>
                </Avatar>
                <div>
                  <h4 className="text-lg mb-1">{post.author.name}</h4>
                  <p className="text-sm text-gray-600">{post.author.role}</p>
                  <p className="text-sm text-gray-600">{post.author.followers} followers</p>
                </div>
                <Button className="w-full">Follow</Button>
                <p className="text-sm text-gray-600">
                  Sharing my NEET preparation journey and helping fellow aspirants achieve their dreams! 🎯
                </p>
              </CardContent>
            </Card>

            {/* More from Author */}
            <Card>
              <CardHeader>
                <h3 className="text-lg">More from {post.author.name}</h3>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  'Best Biology Resources for NEET',
                  'My Daily Study Routine',
                  'Dealing with Exam Stress'
                ].map((title, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                    <p className="text-sm line-clamp-2">{title}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Related Posts */}
            <Card>
              <CardHeader>
                <h3 className="text-lg">Related Posts</h3>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { title: 'Chemistry Study Tips', tag: 'NEET' },
                  { title: 'Physics Problem Solving', tag: 'JEE' },
                  { title: 'Time Management Hacks', tag: 'Study Tips' }
                ].map((post, idx) => (
                  <div key={idx} className="space-y-2">
                    <p className="text-sm hover:text-blue-600 transition-colors cursor-pointer">
                      {post.title}
                    </p>
                    <Badge variant="secondary" className="text-xs">
                      {post.tag}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
