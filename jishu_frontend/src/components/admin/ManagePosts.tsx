import { useState } from 'react';
import Header from '../Header';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../ui/alert-dialog';
import { 
  Search, 
  Eye, 
  Trash2,
  MessageCircle,
  Heart,
  Flag,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { toast } from 'sonner@2.0.3';

interface ManagePostsProps {
  user: any;
}

export default function ManagePosts({ user }: ManagePostsProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState('posts');
  
  const [posts, setPosts] = useState([
    {
      id: 1,
      author: 'Priya Sharma',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Priya',
      title: 'How I Improved My Biology Score by 30%',
      content: 'Here are 5 proven strategies that helped me...',
      likes: 234,
      comments: 45,
      views: 1240,
      date: '2025-02-08',
      status: 'active',
      reported: 0
    },
    {
      id: 2,
      author: 'Rahul Kumar',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rahul',
      title: 'Time Management Tips for JEE Preparation',
      content: 'Balancing school, coaching, and self-study can be...',
      likes: 189,
      comments: 32,
      views: 890,
      date: '2025-02-08',
      status: 'active',
      reported: 1
    },
    {
      id: 3,
      author: 'Ananya Patel',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Ananya',
      title: 'My NEET Success Story: From 400 to 650',
      content: 'One year ago, I was scoring 400 in mocks...',
      likes: 567,
      comments: 89,
      views: 2340,
      date: '2025-02-07',
      status: 'active',
      reported: 0
    }
  ]);

  const [comments, setComments] = useState([
    {
      id: 1,
      postTitle: 'How I Improved My Biology Score',
      author: 'Aditya Verma',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aditya',
      content: 'This is really helpful! Thanks for sharing!',
      likes: 12,
      date: '2025-02-09',
      status: 'active',
      reported: 0
    },
    {
      id: 2,
      postTitle: 'Time Management Tips',
      author: 'Neha Kapoor',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Neha',
      content: 'Could you share more details about the second strategy?',
      likes: 8,
      date: '2025-02-09',
      status: 'active',
      reported: 2
    }
  ]);

  const filteredPosts = posts.filter(post =>
    post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    post.author.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredComments = comments.filter(comment =>
    comment.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    comment.author.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeletePost = (postId: number) => {
    setPosts(posts.filter(post => post.id !== postId));
    toast.success('Post deleted successfully!');
  };

  const handleTogglePostStatus = (postId: number) => {
    setPosts(posts.map(post =>
      post.id === postId
        ? { ...post, status: post.status === 'active' ? 'hidden' : 'active' }
        : post
    ));
    toast.success('Post status updated!');
  };

  const handleDeleteComment = (commentId: number) => {
    setComments(comments.filter(comment => comment.id !== commentId));
    toast.success('Comment deleted successfully!');
  };

  const handleClearReports = (type: 'post' | 'comment', id: number) => {
    if (type === 'post') {
      setPosts(posts.map(post =>
        post.id === id ? { ...post, reported: 0 } : post
      ));
    } else {
      setComments(comments.map(comment =>
        comment.id === id ? { ...comment, reported: 0 } : comment
      ));
    }
    toast.success('Reports cleared!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2">Manage Posts & Comments</h1>
          <p className="text-xl text-gray-600">Moderate community content</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Posts</p>
                  <p className="text-3xl">{posts.length}</p>
                </div>
                <MessageCircle className="w-10 h-10 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Comments</p>
                  <p className="text-3xl">{comments.length}</p>
                </div>
                <MessageCircle className="w-10 h-10 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Likes</p>
                  <p className="text-3xl">{posts.reduce((sum, p) => sum + p.likes, 0)}</p>
                </div>
                <Heart className="w-10 h-10 text-red-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Reported Items</p>
                  <p className="text-3xl text-red-600">
                    {posts.reduce((sum, p) => sum + p.reported, 0) + 
                     comments.reduce((sum, c) => sum + c.reported, 0)}
                  </p>
                </div>
                <Flag className="w-10 h-10 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <Button
            variant={selectedTab === 'posts' ? 'default' : 'outline'}
            onClick={() => setSelectedTab('posts')}
          >
            Posts
          </Button>
          <Button
            variant={selectedTab === 'comments' ? 'default' : 'outline'}
            onClick={() => setSelectedTab('comments')}
          >
            Comments
          </Button>
          <Button
            variant={selectedTab === 'reported' ? 'default' : 'outline'}
            onClick={() => setSelectedTab('reported')}
          >
            Reported ({posts.filter(p => p.reported > 0).length + comments.filter(c => c.reported > 0).length})
          </Button>
        </div>

        {/* Search */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search posts or comments..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Posts Table */}
        {selectedTab === 'posts' && (
          <Card>
            <CardHeader>
              <CardTitle>All Posts</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Author</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Engagement</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Reports</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPosts.map((post) => (
                    <TableRow key={post.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Avatar className="w-8 h-8">
                            <AvatarImage src={post.authorAvatar} />
                            <AvatarFallback>{post.author.charAt(0)}</AvatarFallback>
                          </Avatar>
                          <span className="text-sm">{post.author}</span>
                        </div>
                      </TableCell>
                      <TableCell className="max-w-xs">
                        <p className="truncate">{post.title}</p>
                        <p className="text-xs text-gray-600 truncate">{post.content}</p>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-3 text-sm">
                          <span className="flex items-center gap-1">
                            <Heart className="w-4 h-4" /> {post.likes}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageCircle className="w-4 h-4" /> {post.comments}
                          </span>
                          <span className="flex items-center gap-1">
                            <Eye className="w-4 h-4" /> {post.views}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>{post.date}</TableCell>
                      <TableCell>
                        <Badge 
                          variant={post.status === 'active' ? 'default' : 'secondary'}
                          className="cursor-pointer"
                          onClick={() => handleTogglePostStatus(post.id)}
                        >
                          {post.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {post.reported > 0 ? (
                          <Badge variant="destructive" className="flex items-center gap-1 w-fit">
                            <Flag className="w-3 h-3" />
                            {post.reported}
                          </Badge>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          {post.reported > 0 && (
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleClearReports('post', post.id)}
                            >
                              <CheckCircle2 className="w-4 h-4 text-green-600" />
                            </Button>
                          )}
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <Trash2 className="w-4 h-4 text-red-600" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Post?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  This will permanently delete "{post.title}" and all its comments.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={() => handleDeletePost(post.id)}>
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Comments Table */}
        {selectedTab === 'comments' && (
          <Card>
            <CardHeader>
              <CardTitle>All Comments</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Author</TableHead>
                    <TableHead>Post</TableHead>
                    <TableHead>Comment</TableHead>
                    <TableHead>Likes</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Reports</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredComments.map((comment) => (
                    <TableRow key={comment.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Avatar className="w-8 h-8">
                            <AvatarImage src={comment.authorAvatar} />
                            <AvatarFallback>{comment.author.charAt(0)}</AvatarFallback>
                          </Avatar>
                          <span className="text-sm">{comment.author}</span>
                        </div>
                      </TableCell>
                      <TableCell className="max-w-xs">
                        <p className="text-sm truncate">{comment.postTitle}</p>
                      </TableCell>
                      <TableCell className="max-w-sm">
                        <p className="text-sm truncate">{comment.content}</p>
                      </TableCell>
                      <TableCell>{comment.likes}</TableCell>
                      <TableCell>{comment.date}</TableCell>
                      <TableCell>
                        {comment.reported > 0 ? (
                          <Badge variant="destructive" className="flex items-center gap-1 w-fit">
                            <Flag className="w-3 h-3" />
                            {comment.reported}
                          </Badge>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {comment.reported > 0 && (
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => handleClearReports('comment', comment.id)}
                            >
                              <CheckCircle2 className="w-4 h-4 text-green-600" />
                            </Button>
                          )}
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <Trash2 className="w-4 h-4 text-red-600" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Comment?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  This will permanently delete this comment.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={() => handleDeleteComment(comment.id)}>
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Reported Items */}
        {selectedTab === 'reported' && (
          <Card>
            <CardHeader>
              <CardTitle>Reported Items</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {posts.filter(p => p.reported > 0).length === 0 && comments.filter(c => c.reported > 0).length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle2 className="w-16 h-16 text-green-600 mx-auto mb-4" />
                  <h3 className="text-xl mb-2">No Reported Items</h3>
                  <p className="text-gray-600">All clear! No posts or comments have been reported.</p>
                </div>
              ) : (
                <>
                  {posts.filter(p => p.reported > 0).map(post => (
                    <Card key={`post-${post.id}`} className="border-red-200">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="destructive">Post</Badge>
                              <Badge variant="destructive">{post.reported} reports</Badge>
                            </div>
                            <h4 className="mb-1">{post.title}</h4>
                            <p className="text-sm text-gray-600 mb-2">{post.content}</p>
                            <p className="text-xs text-gray-500">By {post.author} on {post.date}</p>
                          </div>
                          <div className="flex gap-2">
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => handleClearReports('post', post.id)}
                            >
                              <CheckCircle2 className="w-4 h-4 mr-2" />
                              Clear
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleDeletePost(post.id)}
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {comments.filter(c => c.reported > 0).map(comment => (
                    <Card key={`comment-${comment.id}`} className="border-red-200">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge variant="destructive">Comment</Badge>
                              <Badge variant="destructive">{comment.reported} reports</Badge>
                            </div>
                            <p className="text-sm mb-2">{comment.content}</p>
                            <p className="text-xs text-gray-500">On "{comment.postTitle}" by {comment.author} on {comment.date}</p>
                          </div>
                          <div className="flex gap-2">
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => handleClearReports('comment', comment.id)}
                            >
                              <CheckCircle2 className="w-4 h-4 mr-2" />
                              Clear
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleDeleteComment(comment.id)}
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
