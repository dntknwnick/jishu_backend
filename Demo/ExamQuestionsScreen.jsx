import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, FlatList, Alert, Modal, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { questionsAPI, examAttemptsAPI, userAnswersAPI, userExamsAPI } from '../services/api';

const ExamQuestionsScreen = ({ route }) => {
  const {
    subjectId,
    subjectName,
    categoryId,
    category,
    isFullMock,
    userExamId,
    questionCount = 50
  } = route.params;

  const navigation = useNavigation();
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [markedForReview, setMarkedForReview] = useState({});
  const [modalVisible, setModalVisible] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [attemptId, setAttemptId] = useState(null);

  // Fetch questions from the API
  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true);
      setError(null);
      try {
        // Start a new exam attempt
        let attemptResponse;
        try {
          if (userExamId) {
            // If we have a userExamId, create a new attempt for the existing user exam
            attemptResponse = await examAttemptsAPI.startExam(userExamId);
            console.log('Started new attempt for existing exam:', attemptResponse);
          } else {
            // For new exams, we would need to purchase it first, but for now we'll use mock data
            console.log('Using mock attempt for new exam');

            // Try to purchase the exam first
            try {
              const purchaseResponse = await userExamsAPI.purchaseExam(subjectId);
              console.log('Auto-purchased exam:', purchaseResponse);
              if (purchaseResponse && purchaseResponse.exam) {
                attemptResponse = await examAttemptsAPI.startExam(purchaseResponse.exam.id);
              } else {
                attemptResponse = await examAttemptsAPI.startExam(Date.now());
              }
            } catch (purchaseError) {
              console.error('Error auto-purchasing exam:', purchaseError);
              attemptResponse = await examAttemptsAPI.startExam(Date.now());
            }
          }

          setAttemptId(attemptResponse.id);
        } catch (attemptError) {
          console.error('Error starting exam attempt:', attemptError);
          // Create a mock attempt ID as fallback
          attemptResponse = { id: Date.now() };
          setAttemptId(attemptResponse.id);
        }

        // Ensure subjectId is a number for the API call
        const subjectIdParam = subjectId ? (typeof subjectId === 'string' ? parseInt(subjectId, 10) : subjectId) : 1;
        console.log(`Fetching questions for subject ${subjectIdParam}, count: ${questionCount}`);

        try {
          // Fetch questions for this subject
          const response = await questionsAPI.getForExam(subjectIdParam, questionCount);
          console.log(`Fetched ${response.length} questions for subject ${subjectIdParam}`);

          if (Array.isArray(response) && response.length > 0) {
            // Format the questions
            const formattedQuestions = response.map(q => ({
              id: q.id,
              question: q.text,
              options: [
                { id: 'A', text: q.option_a },
                { id: 'B', text: q.option_b },
                { id: 'C', text: q.option_c },
                { id: 'D', text: q.option_d }
              ],
              correctOption: q.correct_option,
              explanation: q.explanation
            }));

            setQuestions(formattedQuestions);
          } else {
            console.error('No questions returned from API');
            setError('No questions available for this exam. Please try again later.');
            setQuestions([]);
          }
        } catch (questionError) {
          console.error('Error fetching questions:', questionError);
          setError('Failed to load questions. Please try again later.');
          setQuestions([]);
        }
        setLoading(false);
      } catch (err) {
        console.error('Error fetching questions:', err);
        setError('Failed to load questions. Please try again.');
        setQuestions([]);
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [subjectId, category, isFullMock, userExamId, questionCount]);



  useEffect(() => {
    // Start a timer that counts up from 0
    const timer = setInterval(() => {
      setTimeElapsed(prevTime => prevTime + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours > 0 ? hours + ':' : ''}${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswer = (option) => {
    setAnswers({ ...answers, [currentQuestionIndex]: option.id });

    // Automatically move to the next question after selecting an option
    if (currentQuestionIndex < questions.length - 1) {
      // Use setTimeout to give a very short delay for better UX
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }, 100); // Very short delay, just enough for the selection to be visible
    }
  };

  const handleMarkForReview = () => {
    setMarkedForReview((prev) => {
      const newState = {
        ...prev,
        [currentQuestionIndex]: !prev[currentQuestionIndex],
      };

      // Check if we're marking (not unmarking) the question
      const isMarking = !prev[currentQuestionIndex];

      // Automatically move to the next question after marking for review
      if (isMarking && currentQuestionIndex < questions.length - 1) {
        // Use setTimeout to give a very short delay for better UX
        setTimeout(() => {
          setCurrentQuestionIndex(currentQuestionIndex + 1);
        }, 100); // Very short delay, just enough for the marking to be visible
      }

      return newState;
    });
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = () => {
    // Calculate score based on correct answers
    const answersArray = Object.entries(answers).map(([index, answer]) => ({
      questionId: questions[parseInt(index)].id,
      selectedOption: answer,
      isCorrect: answer === questions[parseInt(index)].correctOption
    }));

    const score = answersArray.filter(a => a.isCorrect).length;
    const totalQuestions = questions.length;
    const wrongAnswers = answersArray.filter(a => !a.isCorrect).length;
    const unattempted = totalQuestions - answersArray.length;
    const percentage = totalQuestions > 0 ? (score / totalQuestions) * 100 : 0;

    Alert.alert('Submit Test', 'Are you sure you want to submit?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Submit',
        onPress: async () => {
          try {
            // Format answers for submission with enhanced data
            const formattedAnswers = Object.entries(answers).map(([index, selectedOption]) => ({
              question_id: questions[parseInt(index)].id,
              selected_option: selectedOption,
              time_spent_seconds: Math.floor(Math.random() * 120) + 30 // Mock time spent between 30-150 seconds
            }));

            // Submit the exam attempt with enhanced scoring
            let enhancedResults = null;
            if (attemptId) {
              try {
                const submitResponse = await examAttemptsAPI.submitExam(attemptId, formattedAnswers, timeElapsed);
                console.log('Exam submitted successfully:', submitResponse);
                enhancedResults = submitResponse;
              } catch (submitError) {
                console.error('Error submitting exam:', submitError);
                // Continue with local processing even if API submission fails
              }
            }

            // Update local storage for offline access
            try {
              const storedExams = await AsyncStorage.getItem('subscribedExams');

              if (storedExams) {
                const exams = JSON.parse(storedExams);

                // Try to find the exam by subjectId
                const examIndex = exams.findIndex(exam => exam.subjectId === subjectId);

                if (examIndex !== -1) {
                  // Update existing exam
                  console.log('Updating existing exam in purchased list');
                  const updatedExams = [...exams];
                  updatedExams[examIndex] = {
                    ...updatedExams[examIndex],
                    score: score,
                    totalQuestions: totalQuestions,
                    lastAttemptDate: new Date().toISOString(),
                    attemptCount: (updatedExams[examIndex].attemptCount || 0) + 1,
                    completed: true,
                    correctAnswers: score,
                    wrongAnswers: wrongAnswers,
                    unattempted: unattempted
                  };

                  await AsyncStorage.setItem('subscribedExams', JSON.stringify(updatedExams));
                } else {
                  // If exam not found, add it to the list
                  console.log('Adding completed exam to purchased list');
                  const newExam = {
                    id: Date.now().toString(),
                    title: subjectName,
                    description: `${category} ${subjectName} ${isFullMock ? 'Full Mock Test' : 'Practice Test'}`,
                    score: score,
                    totalQuestions: totalQuestions,
                    lastAttemptDate: new Date().toISOString(),
                    attemptCount: 1,
                    completed: true,
                    subjectId: subjectId,
                    category: category,
                    categoryName: category,
                    correctAnswers: score,
                    wrongAnswers: wrongAnswers,
                    unattempted: unattempted
                  };

                  exams.push(newExam);
                  await AsyncStorage.setItem('subscribedExams', JSON.stringify(exams));
                }
              } else {
                // If no exams stored yet, create a new array with this exam
                console.log('Creating new purchased exams list');
                const newExam = {
                  id: Date.now().toString(),
                  title: subjectName,
                  description: `${category} ${subjectName} ${isFullMock ? 'Full Mock Test' : 'Practice Test'}`,
                  score: score,
                  totalQuestions: totalQuestions,
                  lastAttemptDate: new Date().toISOString(),
                  attemptCount: 1,
                  completed: true,
                  subjectId: subjectId,
                  category: category,
                  categoryName: category,
                  correctAnswers: score,
                  wrongAnswers: wrongAnswers,
                  unattempted: unattempted
                };

                await AsyncStorage.setItem('subscribedExams', JSON.stringify([newExam]));
              }
            } catch (storageError) {
              console.error('Error updating purchased exams:', storageError);
            }

            // Navigate to achievements screen with enhanced results
            const examResults = {
              subject: subjectName,
              score,
              totalQuestions,
              correctAnswers: score,
              wrongAnswers,
              unattempted,
              timeTaken: timeElapsed,
              percentage: Math.round(percentage),
              returnToDashboard: true,
              // Include enhanced results if available
              ...(enhancedResults && {
                enhancedResults: {
                  percentage: enhancedResults.percentage,
                  avgTimePerQuestion: enhancedResults.avg_time_per_question,
                  performanceMetrics: enhancedResults.performance_metrics,
                  subjectPerformance: enhancedResults.subject_performance,
                  attemptId: enhancedResults.id
                }
              })
            };

            navigation.navigate('Achivements', {
              attendedExam: examResults
            });
          } catch (error) {
            console.error('Error updating exam record:', error);
            // Still navigate even if there's an error
            navigation.navigate('Achivements', {
              attendedExam: {
                subject: subjectName,
                score,
                totalQuestions,
                correctAnswers: score,
                wrongAnswers,
                unattempted,
                timeTaken: timeElapsed,
                percentage: Math.round(percentage),
                returnToDashboard: true
              }
            });
          }
        }
      },
    ]);
  };



  const handleQuestionSelect = (index) => {
    setCurrentQuestionIndex(index);
    setModalVisible(false);
  };

  return (
    <View style={styles.container}>
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3461eb" />
          <Text style={styles.loadingText}>Loading questions...</Text>
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={{ color: '#fff' }}>Go Back</Text>
          </TouchableOpacity>
        </View>
      ) : questions.length === 0 ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>No questions available for this exam.</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={{ color: '#fff' }}>Go Back</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          {/* Top Bar */}
          <View style={styles.topBar}>
            <TouchableOpacity onPress={handlePrevious}>
              <MaterialCommunityIcons name="chevron-left" size={32} color="#000" />
            </TouchableOpacity>
            <Text style={styles.timer}>{formatTime(timeElapsed)}</Text>
            <TouchableOpacity onPress={() => setModalVisible(true)}>
              <MaterialCommunityIcons name="information-outline" size={28} color="#000" />
            </TouchableOpacity>
            <TouchableOpacity onPress={handleNext}>
              <MaterialCommunityIcons name="chevron-right" size={32} color="#000" />
            </TouchableOpacity>
          </View>

          {/* Question & Options */}
          <Text style={styles.question}>{questions[currentQuestionIndex].question}</Text>
          {questions[currentQuestionIndex].options.map((option, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.option, answers[currentQuestionIndex] === option.id ? styles.selectedOption : null]}
              onPress={() => handleAnswer(option)}
            >
              <Text style={styles.optionLabel}>{option.id}.</Text>
              <Text style={[styles.optionText, answers[currentQuestionIndex] === option.id ? { color: '#fff' } : {}]}>
                {option.text}
              </Text>
            </TouchableOpacity>
          ))}

          {/* Mark for Review Button */}
          <TouchableOpacity onPress={handleMarkForReview} style={styles.markButton}>
            <Text style={{ color: '#fff' }}>{markedForReview[currentQuestionIndex] ? 'Unmark' : 'Mark for Review'}</Text>
          </TouchableOpacity>

          {/* Submit Button at the Bottom */}
          <View style={styles.submitContainer}>
            <TouchableOpacity onPress={handleSubmit} style={styles.submitButton}>
              <Text style={styles.submitText}>Submit</Text>
            </TouchableOpacity>
          </View>
        </>
      )}

      {/* Question Summary Modal */}
      {!loading && !error && questions.length > 0 && (
        <Modal visible={modalVisible} transparent animationType="slide">
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Question Summary</Text>

              {/* Status Legend */}
              <View style={styles.legendContainer}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendBox, { backgroundColor: '#4CAF50' }]} />
                  <Text style={styles.legendText}>Answered</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendBox, { backgroundColor: '#F44336' }]} />
                  <Text style={styles.legendText}>Unanswered</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendBox, { backgroundColor: '#FFC107' }]} />
                  <Text style={styles.legendText}>Marked for Review</Text>
                </View>
              </View>
              <View style={[styles.legendContainer, { marginTop: -5 }]}>
                <View style={styles.legendItem}>
                  <View style={styles.diagonalLegendBox}>
                    {/* Top-left half (Answered - Green) */}
                    <View
                      style={[
                        styles.diagonalHalf,
                        {
                          backgroundColor: '#4CAF50',
                          top: 0,
                          left: 0,
                          right: '50%',
                          bottom: '50%',
                          transform: [{ rotate: '0deg' }]
                        }
                      ]}
                    />
                    {/* Bottom-right half (Marked for Review - Yellow) */}
                    <View
                      style={[
                        styles.diagonalHalf,
                        {
                          backgroundColor: '#FFC107',
                          top: '50%',
                          left: '50%',
                          right: 0,
                          bottom: 0,
                          transform: [{ rotate: '0deg' }]
                        }
                      ]}
                    />
                    {/* Diagonal line */}
                    <View
                      style={{
                        position: 'absolute',
                        width: 1,
                        backgroundColor: '#333',
                        height: '141%', // √2 * 100% to cover the diagonal
                        top: '-20%',
                        left: '50%',
                        transform: [{ rotate: '45deg' }],
                        transformOrigin: 'top left'
                      }}
                    />
                  </View>
                  <Text style={styles.legendText}>Answered & Marked</Text>
                </View>
              </View>

              {/* Question Statistics */}
              <View style={styles.statsContainer}>
                <View style={styles.statItem}>
                  <Text style={styles.statCount}>
                    {Object.keys(answers).filter(key => !markedForReview[key]).length}
                  </Text>
                  <Text style={styles.statLabel}>Answered</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statCount}>
                    {questions.length - Object.keys(answers).length - Object.keys(markedForReview).filter(key => !answers[key]).length}
                  </Text>
                  <Text style={styles.statLabel}>Unanswered</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statCount}>
                    {Object.keys(markedForReview).filter(key => !answers[key]).length}
                  </Text>
                  <Text style={styles.statLabel}>Marked</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statCount}>
                    {Object.keys(answers).filter(key => markedForReview[key]).length}
                  </Text>
                  <Text style={styles.statLabel}>Ans & Marked</Text>
                </View>
              </View>

              {/* Question Grid */}
              <ScrollView style={styles.gridScrollView}>
                <View style={styles.gridContainer}>
                  {questions.map((_, index) => {
                    // Check if question is both answered and marked for review
                    const isAnswered = !!answers[index];
                    const isMarkedForReview = !!markedForReview[index];
                    const isAnsweredAndMarked = isAnswered && isMarkedForReview;

                    // Determine the status and color of each question box
                    let backgroundColor = '#F44336'; // Default: Unanswered (red)

                    if (isAnsweredAndMarked) {
                      // For questions that are both answered and marked for review,
                      // we'll render a special diagonally split box
                      return (
                        <TouchableOpacity
                          key={index}
                          style={[styles.questionBox]}
                          onPress={() => handleQuestionSelect(index)}
                        >
                          <View style={styles.diagonalContainer}>
                            {/* Top-left half (Answered - Green) */}
                            <View
                              style={[
                                styles.diagonalHalf,
                                {
                                  backgroundColor: '#4CAF50',
                                  top: 0,
                                  left: 0,
                                  right: '50%',
                                  bottom: '50%',
                                  transform: [{ rotate: '0deg' }]
                                }
                              ]}
                            />
                            {/* Bottom-right half (Marked for Review - Yellow) */}
                            <View
                              style={[
                                styles.diagonalHalf,
                                {
                                  backgroundColor: '#FFC107',
                                  top: '50%',
                                  left: '50%',
                                  right: 0,
                                  bottom: 0,
                                  transform: [{ rotate: '0deg' }]
                                }
                              ]}
                            />
                            {/* Diagonal line */}
                            <View
                              style={{
                                position: 'absolute',
                                width: 1.5,
                                backgroundColor: '#333',
                                height: '141%', // √2 * 100% to cover the diagonal
                                top: '-20%',
                                left: '50%',
                                transform: [{ rotate: '45deg' }],
                                transformOrigin: 'top left'
                              }}
                            />
                          </View>
                          <Text style={styles.questionBoxText}>{index + 1}</Text>
                        </TouchableOpacity>
                      );
                    } else {
                      // For other questions, use the standard coloring
                      if (isAnswered) {
                        backgroundColor = '#4CAF50'; // Answered (green)
                      } else if (isMarkedForReview) {
                        backgroundColor = '#FFC107'; // Marked for review (yellow)
                      }

                      return (
                        <TouchableOpacity
                          key={index}
                          style={[styles.questionBox, { backgroundColor }]}
                          onPress={() => handleQuestionSelect(index)}
                        >
                          <Text style={styles.questionBoxText}>{index + 1}</Text>
                        </TouchableOpacity>
                      );
                    }
                  })}
                </View>
              </ScrollView>

              <TouchableOpacity onPress={() => setModalVisible(false)} style={styles.closeButton}>
                <Text style={{ color: '#fff' }}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: '#fff' },
  topBar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  timer: { fontSize: 18, fontWeight: 'bold', color: '#3461eb' },
  question: { fontSize: 20, fontWeight: 'bold', marginBottom: 10 },
  option: { flexDirection: 'row', padding: 15, borderWidth: 1, borderColor: '#ccc', borderRadius: 8, marginVertical: 5, alignItems: 'center' },
  optionLabel: { fontWeight: 'bold', marginRight: 8 },
  optionText: { flex: 1 },
  selectedOption: { backgroundColor: '#3461eb', borderColor: '#3461eb' },
  markButton: { backgroundColor: '#3461eb', padding: 10, borderRadius: 8, alignItems: 'center', marginTop: 10 },

  // Loading and error states
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 10, fontSize: 16, color: '#666' },
  errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  errorText: { fontSize: 16, color: 'red', textAlign: 'center', marginBottom: 20 },
  retryButton: { backgroundColor: '#3461eb', paddingVertical: 10, paddingHorizontal: 20, borderRadius: 8 },

  // Submit button styles (fixed at the bottom)
  submitContainer: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20
  },
  submitButton: {
    backgroundColor: '#3461eb',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  submitText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },

  // Modal styles
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)'
  },
  modalContent: {
    width: '90%',
    maxHeight: '80%',
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center'
  },
  closeButton: {
    marginTop: 15,
    backgroundColor: '#3461eb',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
    alignSelf: 'center',
    width: '50%'
  },

  // Grid layout styles
  legendContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 15,
    paddingHorizontal: 10,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  legendBox: {
    width: 16,
    height: 16,
    borderRadius: 4,
    marginRight: 6,
  },
  legendText: {
    fontSize: 12,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 15,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 15,
  },
  statItem: {
    alignItems: 'center',
  },
  statCount: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  gridScrollView: {
    maxHeight: 300,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingHorizontal: 5,
  },
  questionBox: {
    width: '18%', // 5 boxes per row with some spacing
    aspectRatio: 1,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 5,
    margin: '1%',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  questionBoxText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
    zIndex: 2, // Ensure text is above the diagonal background
  },
  diagonalContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    overflow: 'hidden',
    borderRadius: 5,
  },
  // Base style for diagonal halves
  diagonalHalf: {
    position: 'absolute',
    width: '150%', // Make sure it covers the entire box
    height: '150%',
  },
  diagonalLegendBox: {
    width: 16,
    height: 16,
    borderRadius: 4,
    marginRight: 6,
    overflow: 'hidden',
    position: 'relative',
  },
});

export default ExamQuestionsScreen;
