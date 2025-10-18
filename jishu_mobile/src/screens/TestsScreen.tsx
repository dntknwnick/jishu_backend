import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const TestsScreen = () => {
  const [activeTab, setActiveTab] = useState<'available' | 'completed'>('available');

  const availableTests = [
    {
      id: '1',
      subject: 'Physics',
      title: 'Mock Test #1',
      questions: 45,
      duration: 60,
      difficulty: 'Medium',
      color: '#6366f1',
    },
    {
      id: '2',
      subject: 'Chemistry',
      title: 'Mock Test #2',
      questions: 45,
      duration: 60,
      difficulty: 'Hard',
      color: '#10b981',
    },
    {
      id: '3',
      subject: 'Biology',
      title: 'Mock Test #3',
      questions: 90,
      duration: 90,
      difficulty: 'Easy',
      color: '#f59e0b',
    },
  ];

  const completedTests = [
    {
      id: '1',
      subject: 'Physics',
      title: 'Mock Test #5',
      score: 85,
      date: '2 days ago',
      accuracy: 88,
    },
    {
      id: '2',
      subject: 'Chemistry',
      title: 'Mock Test #4',
      score: 92,
      date: '5 days ago',
      accuracy: 95,
    },
  ];

  const renderAvailableTests = () => (
    <View style={styles.testsContainer}>
      {availableTests.map((test) => (
        <TouchableOpacity key={test.id} style={styles.testCard}>
          <View style={[styles.testColorBar, { backgroundColor: test.color }]} />
          <View style={styles.testContent}>
            <View style={styles.testHeader}>
              <View>
                <Text style={styles.testSubject}>{test.subject}</Text>
                <Text style={styles.testTitle}>{test.title}</Text>
              </View>
              <View style={[styles.difficultyBadge, { backgroundColor: `${test.color}20` }]}>
                <Text style={[styles.difficultyText, { color: test.color }]}>
                  {test.difficulty}
                </Text>
              </View>
            </View>

            <View style={styles.testMeta}>
              <View style={styles.metaItem}>
                <Ionicons name="help-circle-outline" size={18} color="#6b7280" />
                <Text style={styles.metaText}>{test.questions} Questions</Text>
              </View>
              <View style={styles.metaItem}>
                <Ionicons name="time-outline" size={18} color="#6b7280" />
                <Text style={styles.metaText}>{test.duration} min</Text>
              </View>
            </View>

            <TouchableOpacity style={[styles.startButton, { backgroundColor: test.color }]}>
              <Text style={styles.startButtonText}>Start Test</Text>
              <Ionicons name="play" size={20} color="#ffffff" />
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderCompletedTests = () => (
    <View style={styles.testsContainer}>
      {completedTests.map((test) => (
        <TouchableOpacity key={test.id} style={styles.completedCard}>
          <View style={styles.completedHeader}>
            <View style={styles.scoreCircle}>
              <Text style={styles.scoreText}>{test.score}%</Text>
            </View>
            <View style={styles.completedInfo}>
              <Text style={styles.completedSubject}>{test.subject}</Text>
              <Text style={styles.completedTitle}>{test.title}</Text>
              <Text style={styles.completedDate}>{test.date}</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#9ca3af" />
          </View>

          <View style={styles.accuracyBar}>
            <Text style={styles.accuracyLabel}>Accuracy</Text>
            <View style={styles.progressBarContainer}>
              <View style={[styles.accuracyFill, { width: `${test.accuracy}%` }]} />
            </View>
            <Text style={styles.accuracyValue}>{test.accuracy}%</Text>
          </View>
        </TouchableOpacity>
      ))}
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Tabs */}
      <View style={styles.tabsContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'available' && styles.activeTab]}
          onPress={() => setActiveTab('available')}
        >
          <Text style={[styles.tabText, activeTab === 'available' && styles.activeTabText]}>
            Available Tests
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'completed' && styles.activeTab]}
          onPress={() => setActiveTab('completed')}
        >
          <Text style={[styles.tabText, activeTab === 'completed' && styles.activeTabText]}>
            Completed
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {activeTab === 'available' ? renderAvailableTests() : renderCompletedTests()}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  tabsContainer: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    margin: 15,
    marginTop: 10,
    borderRadius: 12,
    padding: 5,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: '#6366f1',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  activeTabText: {
    color: '#ffffff',
  },
  testsContainer: {
    padding: 15,
  },
  testCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    marginBottom: 15,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  testColorBar: {
    height: 6,
  },
  testContent: {
    padding: 20,
  },
  testHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  testSubject: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 5,
  },
  testTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  difficultyBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  difficultyText: {
    fontSize: 12,
    fontWeight: '600',
  },
  testMeta: {
    flexDirection: 'row',
    gap: 20,
    marginBottom: 20,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  metaText: {
    fontSize: 14,
    color: '#6b7280',
  },
  startButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
    paddingVertical: 14,
    borderRadius: 12,
  },
  startButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  completedCard: {
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
  completedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  scoreCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#10b98120',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  scoreText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#10b981',
  },
  completedInfo: {
    flex: 1,
  },
  completedSubject: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 3,
  },
  completedTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 3,
  },
  completedDate: {
    fontSize: 12,
    color: '#9ca3af',
  },
  accuracyBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  accuracyLabel: {
    fontSize: 12,
    color: '#6b7280',
    width: 60,
  },
  progressBarContainer: {
    flex: 1,
    height: 8,
    backgroundColor: '#f3f4f6',
    borderRadius: 4,
    overflow: 'hidden',
  },
  accuracyFill: {
    height: '100%',
    backgroundColor: '#10b981',
    borderRadius: 4,
  },
  accuracyValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1f2937',
    width: 40,
    textAlign: 'right',
  },
});

export default TestsScreen;
