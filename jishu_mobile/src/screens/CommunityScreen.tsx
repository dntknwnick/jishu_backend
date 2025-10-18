import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const CommunityScreen = () => {
  const posts = [
    {
      id: '1',
      author: 'Priya Sharma',
      avatar: null,
      time: '2h ago',
      title: 'How I scored 680+ in NEET Physics',
      excerpt: 'Here are my top 10 strategies for mastering NEET Physics...',
      likes: 156,
      comments: 23,
      isLiked: false,
    },
    {
      id: '2',
      author: 'Rahul Kumar',
      avatar: null,
      time: '5h ago',
      title: 'Best resources for JEE Advanced preparation',
      excerpt: 'After analyzing multiple sources, these are the best...',
      likes: 89,
      comments: 15,
      isLiked: true,
    },
    {
      id: '3',
      author: 'Anjali Singh',
      avatar: null,
      time: '1d ago',
      title: 'My study routine that helped me crack NEET',
      excerpt: 'Consistency is key! Here is my daily routine...',
      likes: 234,
      comments: 45,
      isLiked: false,
    },
  ];

  return (
    <View style={styles.container}>
      {/* Create Post Button */}
      <TouchableOpacity style={styles.createPostButton}>
        <Ionicons name="add-circle" size={24} color="#ffffff" />
        <Text style={styles.createPostText}>Share Your Experience</Text>
      </TouchableOpacity>

      <ScrollView showsVerticalScrollIndicator={false}>
        {posts.map((post) => (
          <View key={post.id} style={styles.postCard}>
            {/* Author Info */}
            <View style={styles.authorSection}>
              <View style={styles.avatarContainer}>
                {post.avatar ? (
                  <Image source={{ uri: post.avatar }} style={styles.avatar} />
                ) : (
                  <View style={styles.avatarPlaceholder}>
                    <Text style={styles.avatarText}>
                      {post.author.charAt(0)}
                    </Text>
                  </View>
                )}
              </View>
              <View style={styles.authorInfo}>
                <Text style={styles.authorName}>{post.author}</Text>
                <Text style={styles.postTime}>{post.time}</Text>
              </View>
              <TouchableOpacity>
                <Ionicons name="ellipsis-horizontal" size={24} color="#9ca3af" />
              </TouchableOpacity>
            </View>

            {/* Post Content */}
            <TouchableOpacity>
              <Text style={styles.postTitle}>{post.title}</Text>
              <Text style={styles.postExcerpt} numberOfLines={2}>
                {post.excerpt}
              </Text>
            </TouchableOpacity>

            {/* Engagement */}
            <View style={styles.engagementSection}>
              <TouchableOpacity style={styles.engagementButton}>
                <Ionicons
                  name={post.isLiked ? 'heart' : 'heart-outline'}
                  size={22}
                  color={post.isLiked ? '#ef4444' : '#6b7280'}
                />
                <Text style={styles.engagementText}>{post.likes}</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.engagementButton}>
                <Ionicons name="chatbubble-outline" size={20} color="#6b7280" />
                <Text style={styles.engagementText}>{post.comments}</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.engagementButton}>
                <Ionicons name="bookmark-outline" size={20} color="#6b7280" />
              </TouchableOpacity>

              <TouchableOpacity style={styles.engagementButton}>
                <Ionicons name="share-outline" size={20} color="#6b7280" />
              </TouchableOpacity>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  createPostButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    backgroundColor: '#6366f1',
    margin: 15,
    marginTop: 10,
    paddingVertical: 15,
    borderRadius: 12,
    shadowColor: '#6366f1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  createPostText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  postCard: {
    backgroundColor: '#ffffff',
    marginHorizontal: 15,
    marginBottom: 15,
    borderRadius: 16,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  authorSection: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  avatarContainer: {
    marginRight: 12,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
  },
  avatarPlaceholder: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#6366f1',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  authorInfo: {
    flex: 1,
  },
  authorName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 2,
  },
  postTime: {
    fontSize: 12,
    color: '#9ca3af',
  },
  postTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  postExcerpt: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
    marginBottom: 15,
  },
  engagementSection: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#f3f4f6',
  },
  engagementButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    marginRight: 20,
  },
  engagementText: {
    fontSize: 14,
    color: '#6b7280',
  },
});

export default CommunityScreen;
