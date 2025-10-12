import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { mcqGenerationAPI } from '../services/api';

const MCQGenerator = () => {
  const [topic, setTopic] = useState('');
  const [subject, setSubject] = useState('');
  const [numQuestions, setNumQuestions] = useState('5');
  const [usePdfContent, setUsePdfContent] = useState(true);
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [aiStatus, setAiStatus] = useState(null);

  // Check AI service status
  const checkAIStatus = async () => {
    try {
      setLoading(true);
      const status = await mcqGenerationAPI.getAIStatus();
      setAiStatus(status);
      Alert.alert(
        'AI Service Status',
        `Status: ${status.status}\nOllama: ${status.dependencies.ollama ? 'Available' : 'Not Available'}\nPDF Files: ${status.pdf_files_count || 0}`
      );
    } catch (error) {
      Alert.alert('Error', `Failed to check AI status: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Generate MCQ questions
  const generateMCQ = async () => {
    if (!topic.trim()) {
      Alert.alert('Error', 'Please enter a topic');
      return;
    }

    const numQuestionsInt = parseInt(numQuestions);
    if (isNaN(numQuestionsInt) || numQuestionsInt < 1 || numQuestionsInt > 20) {
      Alert.alert('Error', 'Number of questions must be between 1 and 20');
      return;
    }

    try {
      setLoading(true);
      setQuestions([]);

      const response = await mcqGenerationAPI.generateMCQ({
        topic: topic.trim(),
        subject: subject.trim() || null,
        num_questions: numQuestionsInt,
        use_pdf_content: usePdfContent,
      });

      if (response.status === 'success' && response.questions) {
        setQuestions(response.questions);
        Alert.alert('Success', `Generated ${response.questions.length} questions successfully!`);
      } else if (response.status === 'partial_success') {
        Alert.alert(
          'Partial Success',
          'Questions were generated but may not be in the expected format. Check the raw content.'
        );
        console.log('Raw content:', response.raw_content);
      } else {
        Alert.alert('Error', response.message || 'Failed to generate questions');
      }
    } catch (error) {
      Alert.alert('Error', `Failed to generate MCQ: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Generate MCQ from PDFs only
  const generateMCQFromPDFs = async () => {
    const numQuestionsInt = parseInt(numQuestions);
    if (isNaN(numQuestionsInt) || numQuestionsInt < 1 || numQuestionsInt > 20) {
      Alert.alert('Error', 'Number of questions must be between 1 and 20');
      return;
    }

    try {
      setLoading(true);
      setQuestions([]);

      const response = await mcqGenerationAPI.generateMCQFromPDFs({
        topic: topic.trim() || null,
        subject: subject.trim() || null,
        num_questions: numQuestionsInt,
      });

      if (response.status === 'success' && response.questions) {
        setQuestions(response.questions);
        Alert.alert(
          'Success',
          `Generated ${response.questions.length} questions from ${response.total_pdfs_processed} PDF files!`
        );
      } else if (response.status === 'partial_success') {
        Alert.alert(
          'Partial Success',
          'Questions were generated but may not be in the expected format.'
        );
      } else {
        Alert.alert('Error', response.message || 'Failed to generate questions from PDFs');
      }
    } catch (error) {
      Alert.alert('Error', `Failed to generate MCQ from PDFs: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderQuestion = (question, index) => (
    <View key={index} style={styles.questionContainer}>
      <Text style={styles.questionNumber}>Question {index + 1}</Text>
      <Text style={styles.questionText}>{question.question}</Text>
      
      {question.options && question.options.map((option, optionIndex) => (
        <View key={optionIndex} style={styles.optionContainer}>
          <Text style={[
            styles.optionText,
            option.startsWith(question.correct_answer) && styles.correctOption
          ]}>
            {option}
          </Text>
        </View>
      ))}
      
      {question.explanation && (
        <View style={styles.explanationContainer}>
          <Text style={styles.explanationLabel}>Explanation:</Text>
          <Text style={styles.explanationText}>{question.explanation}</Text>
        </View>
      )}
      
      {question.difficulty && (
        <Text style={styles.difficultyText}>Difficulty: {question.difficulty}</Text>
      )}
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>MCQ Generator</Text>
      
      {/* AI Status Button */}
      <TouchableOpacity style={styles.statusButton} onPress={checkAIStatus}>
        <Text style={styles.buttonText}>Check AI Status</Text>
      </TouchableOpacity>

      {/* Input Fields */}
      <View style={styles.inputContainer}>
        <Text style={styles.label}>Topic *</Text>
        <TextInput
          style={styles.input}
          value={topic}
          onChangeText={setTopic}
          placeholder="e.g., photosynthesis, algebra, history"
        />
      </View>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>Subject (Optional)</Text>
        <TextInput
          style={styles.input}
          value={subject}
          onChangeText={setSubject}
          placeholder="e.g., Biology, Mathematics, History"
        />
      </View>

      <View style={styles.inputContainer}>
        <Text style={styles.label}>Number of Questions (1-20)</Text>
        <TextInput
          style={styles.input}
          value={numQuestions}
          onChangeText={setNumQuestions}
          placeholder="5"
          keyboardType="numeric"
        />
      </View>

      {/* PDF Content Toggle */}
      <TouchableOpacity
        style={styles.toggleContainer}
        onPress={() => setUsePdfContent(!usePdfContent)}
      >
        <Text style={styles.toggleText}>
          Use PDF Content: {usePdfContent ? 'Yes' : 'No'}
        </Text>
      </TouchableOpacity>

      {/* Action Buttons */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, loading && styles.disabledButton]}
          onPress={generateMCQ}
          disabled={loading}
        >
          <Text style={styles.buttonText}>Generate MCQ</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.secondaryButton, loading && styles.disabledButton]}
          onPress={generateMCQFromPDFs}
          disabled={loading}
        >
          <Text style={styles.buttonText}>Generate from PDFs Only</Text>
        </TouchableOpacity>
      </View>

      {/* Loading Indicator */}
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3461eb" />
          <Text style={styles.loadingText}>Generating questions...</Text>
        </View>
      )}

      {/* Questions Display */}
      {questions.length > 0 && (
        <View style={styles.questionsContainer}>
          <Text style={styles.questionsTitle}>Generated Questions</Text>
          {questions.map(renderQuestion)}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f9f9f9',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
  },
  statusButton: {
    backgroundColor: '#6c757d',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  inputContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#fff',
  },
  toggleContainer: {
    backgroundColor: '#e9ecef',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  toggleText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#495057',
  },
  buttonContainer: {
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#3461eb',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  secondaryButton: {
    backgroundColor: '#28a745',
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  questionsContainer: {
    marginTop: 20,
  },
  questionsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  questionContainer: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  questionNumber: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#3461eb',
    marginBottom: 8,
  },
  questionText: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  optionContainer: {
    marginBottom: 8,
  },
  optionText: {
    fontSize: 14,
    color: '#555',
    paddingLeft: 8,
  },
  correctOption: {
    fontWeight: 'bold',
    color: '#28a745',
  },
  explanationContainer: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
  },
  explanationLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#495057',
    marginBottom: 4,
  },
  explanationText: {
    fontSize: 14,
    color: '#6c757d',
  },
  difficultyText: {
    fontSize: 12,
    color: '#6c757d',
    marginTop: 8,
    fontStyle: 'italic',
  },
});

export default MCQGenerator;
