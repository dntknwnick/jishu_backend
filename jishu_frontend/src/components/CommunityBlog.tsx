import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Header from './Header';
import { Card, CardContent, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import {
  Heart,
  MessageCircle,
  Share2,
  Plus,
  TrendingUp,
  Clock,
  Eye,
  Loader2
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import { Label } from './ui/label';
import { toast } from 'sonner@2.0.3';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchPosts, createPost, likePost } from '../store/slices/communitySlice';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface CommunityBlogProps {
  user: any;
}

// Mock posts removed - now using Redux state

export default function CommunityBlog({ user }: CommunityBlogProps) {
  const dispatch = useAppDispatch();
  const { posts, isLoading, error } = useAppSelector((state) => state.community);

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newPost, setNewPost] = useState({ title: '', content: '', tags: '' });

  useEffect(() => {
    dispatch(fetchPosts());
  }, [dispatch]);

  const toggleLike = async (postId: number) => {
    try {
      await dispatch(likePost(postId)).unwrap();
      toast.success('Post liked!');
    } catch (error) {
      toast.error('Failed to like post');
    }
  };

  const handleCreatePost = async () => {
    if (!newPost.title || !newPost.content) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      const postData = {
        title: newPost.title,
        content: newPost.content,
        tags: newPost.tags.split(',').map(t => t.trim()).filter(t => t)
      };

      await dispatch(createPost(postData)).unwrap();
      setNewPost({ title: '', content: '', tags: '' });
      setIsCreateDialogOpen(false);
      toast.success('Post created successfully!');
    } catch (error) {
      toast.error('Failed to create post');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="flex items-center gap-2">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Loading posts...</span>
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
            <h2 className="text-2xl mb-4">Error Loading Posts</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => dispatch(fetchPosts())}>
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
            <h1 className="text-4xl mb-2">Community Blog</h1>
            <p className="text-xl text-gray-600">Share your journey, learn from others</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button size="lg" className="gap-2">
                <Plus className="w-5 h-5" />
                Create Post
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create a New Post</DialogTitle>
                <DialogDescription>
                  Share your study tips, experiences, or ask questions to the community
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    placeholder="Enter a catchy title"
                    value={newPost.title}
                    onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="content">Content</Label>
                  <Textarea
                    id="content"
                    placeholder="Share your thoughts..."
                    rows={6}
                    value={newPost.content}
                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tags">Tags (comma separated)</Label>
                  <Input
                    id="tags"
                    placeholder="e.g., NEET, Study Tips, Motivation"
                    value={newPost.tags}
                    onChange={(e) => setNewPost({ ...newPost, tags: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreatePost}>Publish Post</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Feed */}
          <div className="lg:col-span-2 space-y-6">
            {posts.map((post) => (
              <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                {post.image && (
                  <ImageWithFallback
                    src={post.image}
                    alt={post.title}
                    className="w-full h-64 object-cover"
                  />
                )}
                <CardHeader>
                  <div className="flex items-center gap-3 mb-4">
                    <Avatar>
                      <AvatarImage src={post.author.avatar} alt={post.author.name} />
                      <AvatarFallback>{post.author.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <h4>{post.author.name}</h4>
                      <p className="text-sm text-gray-600">{post.author.role}</p>
                    </div>
                    <span className="text-sm text-gray-500 flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {post.timeAgo}
                    </span>
                  </div>
                  <Link to={`/post/${post.id}`}>
                    <h2 className="text-2xl hover:text-blue-600 transition-colors mb-2">
                      {post.title}
                    </h2>
                  </Link>
                  <p className="text-gray-600 line-clamp-2">{post.content}</p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {post.tags.map((tag, idx) => (
                      <Badge key={idx} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="flex items-center gap-6">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="gap-2"
                        onClick={() => toggleLike(post.id)}
                      >
                        <Heart className={`w-5 h-5 ${post.isLiked ? 'fill-red-500 text-red-500' : ''}`} />
                        <span>{post.likes}</span>
                      </Button>
                      <Link to={`/post/${post.id}`}>
                        <Button variant="ghost" size="sm" className="gap-2">
                          <MessageCircle className="w-5 h-5" />
                          <span>{post.comments}</span>
                        </Button>
                      </Link>
                      <Button variant="ghost" size="sm" className="gap-2">
                        <Share2 className="w-5 h-5" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Eye className="w-4 h-4" />
                      <span>{post.views}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Trending Topics */}
            <Card>
              <CardHeader>
                <h3 className="text-lg flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Trending Topics
                </h3>
              </CardHeader>
              <CardContent className="space-y-3">
                {['NEET 2025', 'JEE Preparation', 'Study Techniques', 'Time Management', 'Motivation'].map((topic, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                    <span>#{topic}</span>
                    <Badge variant="secondary">{Math.floor(Math.random() * 50) + 10}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Popular Authors */}
            <Card>
              <CardHeader>
                <h3 className="text-lg">Popular Authors</h3>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { name: 'Dr. Amit Gupta', followers: '2.5K', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Amit' },
                  { name: 'Sneha Reddy', followers: '1.8K', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sneha' },
                  { name: 'Rohan Mehta', followers: '1.2K', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rohan' },
                ].map((author, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <Avatar>
                      <AvatarImage src={author.avatar} alt={author.name} />
                      <AvatarFallback>{author.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <h4 className="text-sm">{author.name}</h4>
                      <p className="text-xs text-gray-600">{author.followers} followers</p>
                    </div>
                    <Button size="sm" variant="outline">Follow</Button>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Community Guidelines */}
            <Card className="bg-blue-50 border-blue-200">
              <CardHeader>
                <h3 className="text-lg">Community Guidelines</h3>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-gray-700">
                <p>• Be respectful and supportive</p>
                <p>• Share authentic experiences</p>
                <p>• No spam or promotional content</p>
                <p>• Help others when you can</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
