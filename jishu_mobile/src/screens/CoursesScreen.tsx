import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const CoursesScreen = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const courses = [
    {
      id: '1',
      name: 'NEET',
      subjects: ['Physics', 'Chemistry', 'Biology'],
      totalTests: 450,
      progress: 65,
      icon: '🏥',
      color: '#10b981',
    },
    {
      id: '2',
      name: 'JEE Advanced',
      subjects: ['Physics', 'Chemistry', 'Mathematics'],
      totalTests: 380,
      progress: 45,
      icon: '🎓',
      color: '#6366f1',
    },
    {
      id: '3',
      name: 'JEE Mains',
      subjects: ['Physics', 'Chemistry', 'Mathematics'],
      totalTests: 420,
      progress: 30,
      icon: '📚',
      color: '#f59e0b',
    },
  ];

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#9ca3af" />
        <TextInput
          style={styles.searchInput}
          placeholder="Search courses..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor="#9ca3af"
        />
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* My Courses */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>My Courses</Text>
          {courses.map((course) => (
            <TouchableOpacity key={course.id} style={styles.courseCard}>
              <View style={styles.courseHeader}>
                <View style={styles.courseIcon}>
                  <Text style={styles.courseEmoji}>{course.icon}</Text>
                </View>
                <View style={styles.courseInfo}>
                  <Text style={styles.courseName}>{course.name}</Text>
                  <Text style={styles.courseSubjects}>
                    {course.subjects.join(' • ')}
                  </Text>
                </View>
                <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
              </View>

              {/* Progress Bar */}
              <View style={styles.progressSection}>
                <View style={styles.progressHeader}>
                  <Text style={styles.progressLabel}>Progress</Text>
                  <Text style={styles.progressValue}>{course.progress}%</Text>
                </View>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      {
                        width: `${course.progress}%`,
                        backgroundColor: course.color,
                      },
                    ]}
                  />
                </View>
              </View>

              {/* Stats */}
              <View style={styles.statsRow}>
                <View style={styles.stat}>
                  <Ionicons name="document-text-outline" size={16} color="#6b7280" />
                  <Text style={styles.statText}>{course.totalTests} Tests</Text>
                </View>
                <View style={styles.stat}>
                  <Ionicons name="time-outline" size={16} color="#6b7280" />
                  <Text style={styles.statText}>1 Year Access</Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Explore More Courses */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Explore More</Text>
          <TouchableOpacity style={styles.exploreCard}>
            <View style={styles.exploreIcon}>
              <Ionicons name="add-circle" size={40} color="#6366f1" />
            </View>
            <View style={styles.exploreContent}>
              <Text style={styles.exploreTitle}>Browse All Courses</Text>
              <Text style={styles.exploreText}>
                Discover more courses to boost your preparation
              </Text>
            </View>
            <Ionicons name="arrow-forward" size={24} color="#6366f1" />
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    margin: 15,
    marginTop: 10,
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  searchInput: {
    flex: 1,
    marginLeft: 10,
    fontSize: 16,
    color: '#1f2937',
  },
  section: {
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 15,
  },
  courseCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  courseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  courseIcon: {
    width: 50,
    height: 50,
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  courseEmoji: {
    fontSize: 28,
  },
  courseInfo: {
    flex: 1,
  },
  courseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 5,
  },
  courseSubjects: {
    fontSize: 14,
    color: '#6b7280',
  },
  progressSection: {
    marginBottom: 15,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  progressValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#f3f4f6',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 20,
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  statText: {
    fontSize: 14,
    color: '#6b7280',
  },
  exploreCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#eef2ff',
    borderRadius: 16,
    padding: 20,
    borderWidth: 2,
    borderColor: '#c7d2fe',
    borderStyle: 'dashed',
  },
  exploreIcon: {
    marginRight: 15,
  },
  exploreContent: {
    flex: 1,
  },
  exploreTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 5,
  },
  exploreText: {
    fontSize: 14,
    color: '#6b7280',
  },
});

export default CoursesScreen;
