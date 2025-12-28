import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  Modal,
  Platform,
} from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useHealthStore } from '../src/store/healthStore';
import { t } from '../src/constants/translations';

export default function HomeScreen() {
  const router = useRouter();
  const { user, language, setLanguage, isOnline, syncQueue } = useHealthStore();
  const [showVoiceAssistant, setShowVoiceAssistant] = useState(false);

  const openVoiceAssistant = () => {
    setShowVoiceAssistant(true);
  };

  const closeVoiceAssistant = () => {
    setShowVoiceAssistant(false);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Network Status */}
        <View style={[styles.statusBanner, isOnline ? styles.onlineBanner : styles.offlineBanner]}>
          <MaterialCommunityIcons
            name={isOnline ? 'wifi' : 'wifi-off'}
            size={16}
            color="#ffffff"
          />
          <Text style={styles.statusText}>
            {isOnline ? t('online', language) : t('offline', language)}
          </Text>
          {syncQueue.length > 0 && (
            <Text style={styles.syncText}>
              {' '}• {syncQueue.length} {t('syncPending', language)}
            </Text>
          )}
        </View>

        {/* Language Toggle */}
        <View style={styles.languageToggle}>
          <TouchableOpacity
            style={[styles.langBtn, language === 'bn' && styles.langBtnActive]}
            onPress={() => setLanguage('bn')}
          >
            <Text style={[styles.langText, language === 'bn' && styles.langTextActive]}>
              বাংলা
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.langBtn, language === 'en' && styles.langBtnActive]}
            onPress={() => setLanguage('en')}
          >
            <Text style={[styles.langText, language === 'en' && styles.langTextActive]}>
              English
            </Text>
          </TouchableOpacity>
        </View>

        {/* Welcome Section */}
        <View style={styles.welcomeSection}>
          <MaterialCommunityIcons name="hospital-box" size={80} color="#22c55e" />
          <Text style={styles.appName}>{t('appName', language)}</Text>
          <Text style={styles.tagline}>{t('appTagline', language)}</Text>
        </View>

        {/* Profile Status */}
        {!user ? (
          <TouchableOpacity
            style={styles.profilePrompt}
            onPress={() => router.push('/profile')}
          >
            <MaterialCommunityIcons name="account-plus" size={24} color="#f59e0b" />
            <Text style={styles.profilePromptText}>{t('createProfile', language)}</Text>
            <MaterialCommunityIcons name="chevron-right" size={24} color="#f59e0b" />
          </TouchableOpacity>
        ) : (
          <View style={styles.userCard}>
            <MaterialCommunityIcons name="account-check" size={32} color="#22c55e" />
            <View style={styles.userInfo}>
              <Text style={styles.userName}>
                {user.gender === 'male' ? '👨' : user.gender === 'female' ? '👩' : '🧑'}{' '}
                {user.age} {t('years', language)}
              </Text>
              {user.location && <Text style={styles.userLocation}>{user.location}</Text>}
            </View>
          </View>
        )}

        {/* Main Action Button */}
        <TouchableOpacity
          style={styles.mainButton}
          onPress={() => router.push('/symptoms')}
        >
          <MaterialCommunityIcons name="stethoscope" size={32} color="#ffffff" />
          <Text style={styles.mainButtonText}>{t('checkSymptoms', language)}</Text>
          <Text style={styles.mainButtonSubtext}>
            {language === 'bn'
              ? 'লক্ষণ নির্বাচন করে পরামর্শ নিন'
              : 'Select symptoms to get guidance'}
          </Text>
        </TouchableOpacity>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.quickAction}
            onPress={() => router.push('/history')}
          >
            <MaterialCommunityIcons name="history" size={28} color="#60a5fa" />
            <Text style={styles.quickActionText}>{t('viewHistory', language)}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickAction}
            onPress={() => router.push('/profile')}
          >
            <MaterialCommunityIcons name="account-cog" size={28} color="#a78bfa" />
            <Text style={styles.quickActionText}>{t('profile', language)}</Text>
          </TouchableOpacity>
        </View>

        {/* Disclaimer */}
        <View style={styles.disclaimer}>
          <MaterialCommunityIcons name="alert-circle" size={20} color="#f59e0b" />
          <Text style={styles.disclaimerText}>{t('disclaimer', language)}</Text>
        </View>
      </ScrollView>

      {/* Floating Voice Assistant Button */}
      <TouchableOpacity
        style={styles.floatingVoiceButton}
        onPress={openVoiceAssistant}
        activeOpacity={0.8}
      >
        <MaterialCommunityIcons name="microphone" size={28} color="#ffffff" />
        <Text style={styles.voiceButtonText}>
          {language === 'bn' ? 'ভয়েস' : 'Voice'}
        </Text>
      </TouchableOpacity>

      {/* Voice Assistant Modal */}
      <Modal
        visible={showVoiceAssistant}
        animationType="slide"
        transparent={false}
        onRequestClose={closeVoiceAssistant}
      >
        <SafeAreaView style={styles.modalContainer}>
          {/* Close Button */}
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>
              {language === 'bn' ? 'সুস্থ ভয়েস সহায়ক' : 'Sustho Voice Assistant'}
            </Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={closeVoiceAssistant}
            >
              <MaterialCommunityIcons name="close" size={28} color="#ffffff" />
            </TouchableOpacity>
          </View>

          {/* Voice Assistant - Web Only */}
          {Platform.OS === 'web' ? (
            <iframe
              src="https://sustho-health-voice-assistant-903298187865.us-west1.run.app"
              style={{
                flex: 1,
                width: '100%',
                height: '100%',
                border: 'none',
                backgroundColor: '#ffffff',
              }}
              allow="microphone; geolocation; camera; autoplay"
              sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-modals allow-downloads"
              title="Sustho Voice Assistant"
            />
          ) : (
            <View style={styles.webview}>
              <Text style={styles.webNotSupported}>
                {language === 'bn'
                  ? 'ভয়েস সহায়ক শুধুমাত্র ওয়েব ব্রাউজারে উপলব্ধ'
                  : 'Voice Assistant is only available on web browser'}
              </Text>
            </View>
          )}
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  statusBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 8,
    borderRadius: 8,
    marginBottom: 16,
  },
  onlineBanner: {
    backgroundColor: '#166534',
  },
  offlineBanner: {
    backgroundColor: '#b91c1c',
  },
  statusText: {
    color: '#ffffff',
    marginLeft: 8,
    fontWeight: '600',
  },
  syncText: {
    color: '#fde68a',
    fontSize: 12,
  },
  languageToggle: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 24,
  },
  langBtn: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
  },
  langBtnActive: {
    backgroundColor: '#22c55e',
    borderColor: '#22c55e',
  },
  langText: {
    color: '#94a3b8',
    fontWeight: '600',
  },
  langTextActive: {
    color: '#ffffff',
  },
  welcomeSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  appName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 16,
  },
  tagline: {
    fontSize: 14,
    color: '#94a3b8',
    marginTop: 8,
    textAlign: 'center',
  },
  profilePrompt: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  profilePromptText: {
    flex: 1,
    color: '#f59e0b',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 12,
  },
  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
  },
  userInfo: {
    marginLeft: 12,
  },
  userName: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },
  userLocation: {
    color: '#94a3b8',
    fontSize: 14,
    marginTop: 4,
  },
  mainButton: {
    backgroundColor: '#22c55e',
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    marginBottom: 24,
  },
  mainButtonText: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 12,
  },
  mainButtonSubtext: {
    color: '#bbf7d0',
    fontSize: 14,
    marginTop: 4,
  },
  quickActions: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  quickAction: {
    flex: 1,
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  quickActionText: {
    color: '#ffffff',
    fontSize: 14,
    marginTop: 8,
    fontWeight: '500',
  },
  disclaimer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1c1917',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  disclaimerText: {
    flex: 1,
    color: '#fcd34d',
    fontSize: 12,
    marginLeft: 8,
  },
  floatingVoiceButton: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    backgroundColor: '#2563eb',
    width: 70,
    height: 70,
    borderRadius: 35,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    borderWidth: 3,
    borderColor: '#ffffff',
  },
  voiceButtonText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: '600',
    marginTop: 2,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#1e293b',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  closeButton: {
    backgroundColor: '#ef4444',
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  webview: {
    flex: 1,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  webNotSupported: {
    color: '#64748b',
    fontSize: 16,
    textAlign: 'center',
    padding: 20,
  },
});
