import openai
import streamlit as st
import re
import speech_recognition as sr
from gtts import gTTS
import os
import time
import pygame
import tempfile
import logging
import traceback
import webbrowser
import urllib.parse
import pywhatkit as pwk
import datetime
import base64
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EnerTech-Assistant")

# Debug helper function
def debug_print(message, level="info"):
    """Print debug messages to Streamlit and logs"""
    if level == "error":
        logger.error(message)
        st.error(f"DEBUG ERROR: {message}")
    elif level == "warning":
        logger.warning(message)
        st.warning(f"DEBUG WARNING: {message}")
    else:
        logger.info(message)
        if st.session_state.get('debug_mode', False):
            st.info(f"DEBUG: {message}")

# Your OpenAI API key
openai.api_key = "Open_ai_API_Key"

# YouTube videos data
youtube_videos = [
    {
        "title": "How to Fix Overload Fault in REeFI Solar Hybrid Inverter | Error Code 409",
        "url": "https://youtu.be/0iYbLIsCLUw",
        "description": "This video provides a step-by-step guide to troubleshoot and fix Overload Fault (Error Code 409) in REeFI Solar Hybrid Inverters. It covers common causes like motor or compressor surges, safe shutdown procedures, component inspections (e.g., current transformers and controller cards), and the proper sequence for safe reconnection. Includes EnerTech support contact for further assistance.",
        "keywords": [
            "overload fault", "error code 409", "REeFI inverter", "EnerTech", 
            "solar hybrid inverter", "troubleshooting", "shutdown procedure", 
            "control MCB", "battery MCB", "component inspection"
        ],
        "category": "Troubleshooting"
    },
    
    {
        "title": "How to Change REeFI Solar Hybrid Inverter Mode | Inverter Mode Setup | Choose Right Mode | EnerTech",
        "url": "https://youtu.be/Ia4q2qwxbGE",
        "description": "This instructional video from EnerTech guides users through a safe, step-by-step procedure for changing the mode of a REeFI Solar Hybrid Inverter. It covers complete shutdown steps, battery voltage checks, accessing control settings, navigating inverter mode pages, setting grid charger exports, and verifying the new mode post-reboot. Emphasis is placed on safety and customization, making this video ideal for users aiming to optimize their inverter configuration.",
        "keywords": [
            "REeFI inverter", "inverter mode change", "solar hybrid inverter", "EnerTech", 
            "inverter configuration", "MCB shutdown", "control settings", 
            "grid charger export", "8585 password", "mode verification"
        ],
        "category": "Setup"
    },

    {
        "title": "How to Set Batteryless Mode in EnerTech Solar Hybrid Inverter | Step-by-Step Guide | NTech",
        "url": "https://youtu.be/Ph9NfHAXvb0",
        "description": "This instructional video from NTech walks viewers through the complete process of enabling batteryless mode on an EnerTech Solar Hybrid Inverter. The step-by-step tutorial includes checking the isolation transformer, accessing advanced configuration settings using the 8585 code, adjusting critical voltage parameters, and setting inverter and MPPT modes. It also demonstrates how to enable or disable the battery relay, reboot the system properly, and verify that settings have been applied successfully. Viewers are encouraged to reach out to EnerTech support if issues arise and to engage with the community through likes, shares, and subscriptions.",
        "keywords": [
            "EnerTech inverter", "batteryless inverter setup", "solar hybrid inverter", "NTech", 
            "inverter configuration", "isolation transformer check", "8585 configuration code",
            "battery settings inverter", "MPPT mode", "grid charger setting", 
            "battery relay disable", "inverter reboot", "batteryless mode verification"
        ],
        "category": "Setup"
    },

    {
        "title": "Solar Hybrid Inverter Battery Relay Error | REeFI Solar Hybrid PCU",
        "url": "https://youtu.be/WOui1OeblyI",
        "description": "This instructional video from EnerTech explains how to diagnose and fix battery relay errors in REeFI Solar Hybrid PCUs. It demonstrates the proper shutdown sequence, safety precautions, and troubleshooting steps for relay failures. The tutorial covers checking battery connections, inspecting relay components, testing functionality, and the correct restart procedure. Common causes addressed include loose connections, relay wear, and communication errors. The video emphasizes following proper sequence to prevent damage to the system and offers contact information for EnerTech support if additional assistance is needed.",
        "keywords": [
            "battery relay error", "REeFI inverter", "EnerTech", "solar hybrid PCU", 
            "troubleshooting", "relay failure", "shutdown procedure", "battery connections",
            "system restart", "component inspection", "MCB operation", "safety precautions"
        ],
        "category": "Troubleshooting"
    },

    {
        "title": "EnerTech Grid Export Enable Feature | REeFI Grid Export Enable",
        "url": "https://youtu.be/zQNrE6Xc1uc",
        "description": "This comprehensive guide from EnerTech demonstrates how to enable and configure the Grid Export feature on REeFI Solar Hybrid Inverters. The video walks through accessing the advanced settings menu using the password 8585, navigating to the grid export settings page, and selecting appropriate export parameters based on local regulations and requirements. It explains how the feature allows excess solar energy to be fed back to the utility grid, potentially earning credits through net metering. The tutorial also covers safety considerations, verification steps after enabling the feature, and troubleshooting tips for common configuration issues that might prevent successful grid export.",
        "keywords": [
            "grid export", "REeFI inverter", "EnerTech", "net metering", "solar hybrid inverter", 
            "export settings", "utility grid connection", "configuration password", "excess solar energy", 
            "power export enable", "parameter settings", "solar electricity credits"
        ],
        "category": "Setup"
    },

    {
        "title": "EnerTech Emergency Switch Feature | Solar Hybrid Inverter Emergency Switch",
        "url": "https://youtu.be/-FJAwE1Q2Xw",
        "description": "This tutorial from EnerTech explains the Emergency Switch feature available on their Solar Hybrid Inverters, designed for critical situations requiring immediate system shutdown. The video demonstrates the location and proper operation of the emergency switch, explains its internal mechanism that instantly disconnects all power sources, and outlines scenarios when it should be used. Safety procedures before and after activation are covered in detail, along with the proper restart sequence once the emergency has been resolved. The video emphasizes that this feature should only be used in genuine emergencies to prevent system damage and includes contact information for EnerTech support if users encounter any issues.",
        "keywords": [
            "emergency switch", "safety feature", "EnerTech inverter", "solar hybrid system", 
            "rapid shutdown", "power disconnection", "system safety", "critical situation handling", 
            "restart procedure", "emergency protocols", "power isolation", "safety mechanisms"
        ],
        "category": "Safety"
    },

    {
        "title": "Sunmagic Installation (Solar Hybrid Inverter Installation)",
        "url": "https://youtu.be/2lickIQPba4",
        "description": "This detailed installation guide walks viewers through the complete process of setting up an EnerTech Sunmagic Solar Hybrid Inverter system. The video covers essential pre-installation planning, including site assessment, required tools and components, and safety precautions. It demonstrates step-by-step mounting procedures for the inverter, proper electrical connections for solar panels, batteries, and grid tie-ins, while emphasizing correct wire sizing and terminal connections. The tutorial also shows how to configure initial system settings, perform verification tests, and troubleshoot common installation issues. The video concludes with guidance on system monitoring setup and regular maintenance practices to ensure optimal performance.",
        "keywords": [
            "Sunmagic inverter", "solar installation", "EnerTech", "hybrid system setup", 
            "inverter mounting", "electrical connections", "solar panel wiring", "battery setup", 
            "configuration settings", "system testing", "installation guide", "maintenance procedures"
        ],
        "category": "Installation"
    },

    {
        "title": "Troubleshooting CAN Bus Errors or Communication Error",
        "url": "https://youtu.be/PLvuze1fJOk",
        "description": "This technical troubleshooting video addresses CAN Bus and communication errors in EnerTech Solar Hybrid Inverter systems. It explains how the Controller Area Network (CAN) functions within the inverter system, common causes of communication failures, and systematic diagnostic approaches. The tutorial covers checking physical connections, identifying damaged cables or termination resistors, voltage testing procedures, and software verification steps. Viewers learn how to interpret error codes, reset communication modules, and implement solutions for various communication issues. The video also provides preventive maintenance tips and when to contact EnerTech technical support for advanced troubleshooting assistance.",
        "keywords": [
            "CAN bus error", "communication failure", "troubleshooting", "EnerTech inverter", 
            "diagnostic procedures", "connection verification", "error codes", "terminal resistance", 
            "system reset", "data transmission issues", "cable inspection", "network protocols"
        ],
        "category": "Troubleshooting"
    },

    {
        "title": "EnerTech Solar Hybrid Inverter Without Battery & Without Grid",
        "url": "https://youtu.be/6cub-0mKwyY",
        "description": "This informative video showcases EnerTech's innovative Solar Hybrid Inverter solution that operates without requiring batteries or grid connection. The presentation explains the specialized direct solar configuration, ideal for remote locations or daytime-only operations where traditional setups are impractical. It covers the system architecture, component requirements, installation considerations, and operational principles of this cost-effective solar solution. The video highlights real-world applications including water pumping, agricultural operations, and day-use facilities, while detailing the advantages such as reduced initial investment, simplified maintenance, and elimination of battery replacement costs. Case studies of successful implementations are also presented, demonstrating the versatility and effectiveness of this specialized solar configuration.",
        "keywords": [
            "batteryless solar", "direct solar operation", "EnerTech", "grid-independent", 
            "daytime solar solution", "cost-effective solar", "water pumping application", 
            "remote location power", "simplified solar system", "no-battery operation", 
            "maintenance-free solar", "specialized configuration"
        ],
        "category": "Product Information"
    },

    {
        "title": "Solar Hybrid inverter - 3phase SunMagic+ Installation",
        "url": "https://youtu.be/lNst1tsJYBo",
        "description": "This comprehensive installation guide focuses specifically on EnerTech's 3-phase SunMagic+ Solar Hybrid Inverter systems for commercial and industrial applications. The video provides detailed instructions on proper site preparation, equipment spacing, ventilation requirements, and mounting procedures for these larger systems. It covers three-phase AC wiring diagrams, solar array string configuration, battery bank connections, and proper grounding techniques. The tutorial explains phase balancing, neutral connections, and protection device requirements unique to three-phase systems. Viewers learn about commissioning procedures, system testing protocols, and configuration settings specific to commercial three-phase operations. The video also includes guidance on integration with existing electrical infrastructure and monitoring setup for these more complex installations.",
        "keywords": [
            "3-phase installation", "SunMagic+", "commercial solar", "EnerTech", 
            "industrial inverter setup", "three-phase wiring", "phase balancing", 
            "commercial solar configuration", "three-phase protection", "neutral connections", 
            "commissioning process", "system integration"
        ],
        "category": "Installation"
    },

    {
        "title": "Solar Hybrid Inverter - 1ph SunMagic Installation",
        "url": "https://youtu.be/lywYdHIXLb4",
        "description": "This detailed installation tutorial focuses on the EnerTech SunMagic single-phase solar hybrid inverter for residential and small commercial applications. The video guides viewers through a complete installation process, beginning with site assessment, inverter placement considerations, and mounting requirements. It demonstrates proper wiring connections for solar panels, batteries, and home electrical integration, with emphasis on adherence to electrical codes and safety standards. The tutorial covers initial system configuration, parameter settings optimization, and verification testing procedures. Additional guidance is provided for monitoring setup, understanding display indicators, and basic maintenance procedures. The video concludes with troubleshooting tips for common installation issues and contact information for EnerTech technical support.",
        "keywords": [
            "single-phase installation", "SunMagic inverter", "residential solar", "EnerTech", 
            "home solar setup", "inverter mounting", "battery connections", "panel wiring", 
            "system configuration", "parameter settings", "residential integration", "safety requirements"
        ],
        "category": "Installation"
    },

    {
        "title": "About EnerTech | EnerTech UPS Pvt Ltd | EnerTech Product Range",
        "url": "https://youtu.be/JxaNumEAlJ0",
        "description": "This corporate overview video introduces EnerTech UPS Pvt Ltd, an established Indian manufacturer specializing in solar hybrid inverters and power solutions since 1989. The presentation highlights the company's 30+ years of experience, manufacturing facilities, and comprehensive product range including single and three-phase solar hybrid inverters, UPS systems, and power conditioning units. It showcases EnerTech's technological innovations, quality certifications (including MNRE approval), and customer service network spanning India and international markets. The video also features testimonials from satisfied customers across various sectors and outlines the company's commitment to sustainable energy solutions. Contact information and details about their nationwide service network are provided for potential customers seeking reliable solar power systems.",
        "keywords": [
            "EnerTech company", "solar manufacturer", "Indian power solutions", "company history", 
            "product range", "solar hybrid inverters", "MNRE approved", "customer testimonials", 
            "service network", "UPS systems", "power conditioning", "sustainable energy"
        ],
        "category": "Company Information"
    },

    {
        "title": "How to Change AC Input Voltage Range | EnerTron HF Solar Hybrid Inverter",
        "url": "https://youtu.be/BEu2EV1c6Kw",
        "description": "This technical tutorial demonstrates how to modify the AC input voltage range settings on EnerTron HF Solar Hybrid Inverters to accommodate different grid conditions. The video explains the importance of proper voltage range configuration, potential issues caused by incorrect settings, and when adjustments might be necessary. It provides step-by-step instructions for accessing the system configuration menu, navigating to voltage parameters, and modifying the upper and lower voltage thresholds. Safety precautions and recommended settings for different regions and applications are discussed in detail. The tutorial also covers verification procedures to ensure changes were successfully implemented and explains how these adjustments affect system performance and grid interaction. Contact information for EnerTech technical support is provided for additional assistance.",
        "keywords": [
            "AC voltage settings", "EnerTron HF inverter", "input voltage range", "voltage parameters", 
            "grid compatibility", "configuration menu", "voltage thresholds", "regional settings", 
            "system performance", "voltage adjustment", "grid interaction", "parameter configuration"
        ],
        "category": "Setup"
    }
]

#-----------------------------------------------------------------------------------
# Sound Functions
#-----------------------------------------------------------------------------------

def play_ringing_sound():
    """Play phone ringing sound from specified file"""
    try:
        debug_print("Playing ringing sound from file")
        ringing_sound_path = r"C:\Users\Rupesh Shinde\Desktop\Youtube\phone-ringing-6805.mp3"
        
        # Create a simple visual indicator
        st.markdown("""
        <div style="background-color: #ffe0b2; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <p style="color: #e65100; margin: 0; text-align: center; font-weight: bold;">
                📞 Ringing... Please wait for connection
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Play the actual sound file
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(ringing_sound_path)
            pygame.mixer.music.play()
            
            # Wait for 3 seconds or until sound finishes
            start_time = time.time()
            while pygame.mixer.music.get_busy() and time.time() - start_time < 3:
                pygame.time.Clock().tick(10)
                
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            debug_print("Ringing sound played successfully")
        except Exception as e:
            debug_print(f"Error playing ringing sound file: {e}", "error")
            # Fallback to time delay
            time.sleep(2)
            
        debug_print("Ringing complete")
        return True
    except Exception as e:
        debug_print(f"Error in ringing simulation: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        # Fallback to time delay
        time.sleep(2)
        return False

def play_connected_sound():
    """Play call connected sound - without requiring external files"""
    try:
        debug_print("Playing connected sound (simulated)")
        # Create a simple audio indicator instead of playing actual sounds
        st.markdown("""
        <div style="background-color: #c8e6c9; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <p style="color: #2e7d32; margin: 0; text-align: center; font-weight: bold;">
                📞 Connected to Enertech Support
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Use time delay instead of sound
        time.sleep(1)
        debug_print("Connected indication complete")
        return True
    except Exception as e:
        debug_print(f"Error in connected simulation: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        return False

#-----------------------------------------------------------------------------------
# WhatsApp Integration Function with PyWhatKit - IMPROVED VERSION
#-----------------------------------------------------------------------------------

def send_whatsapp_message(phone_number, message):
    """
    Sends a WhatsApp message using pywhatkit with improved timing and error handling
    
    Parameters:
    - phone_number: Recipient's phone number 
    - message: Message to send
    
    Returns:
    - Boolean indicating success
    """
    try:
        debug_print(f"Preparing to send WhatsApp message to: {phone_number}")
        
        # Clean the phone number - remove any spaces, +, -, or () characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        debug_print(f"Cleaned phone number: {clean_number}")
        
        # Check if the number already has a country code
        if not clean_number.startswith('91') and len(clean_number) < 12:
            # Add India country code (91) by default
            clean_number = '91' + clean_number
            debug_print(f"Added country code: {clean_number}")
            
        # Get current time and add 1 minute (pywhatkit requires future time)
        now = datetime.datetime.now()
        send_time_hour = now.hour
        send_time_minute = now.minute + 1  # Send 1 minute from now
        
        # Adjust if minute rolls over to next hour
        if send_time_minute >= 60:
            send_time_minute %= 60
            send_time_hour += 1
        if send_time_hour >= 24:
            send_time_hour %= 24
            
        debug_print(f"Scheduled time: {send_time_hour}:{send_time_minute}")
        
        # Display a message to the user about what's happening
        st.info("Opening WhatsApp Web to send your message. Please wait and don't interact with the browser.")
        
        # Send the message with improved parameters
        # - wait_time: increased to 30 seconds to allow browser to open
        # - tab_close: set to False to keep the tab open for manual sending if needed
        # - close_time: increased to 5 seconds to allow more time for sending
        debug_print("Sending WhatsApp message via pywhatkit")
        
        # Try to send the message
        pwk.sendwhatmsg(
            f"+{clean_number}", 
            message, 
            send_time_hour, 
            send_time_minute, 
            30,  # wait_time in seconds (increased)
            True,  # tab_close
            5  # close_time in seconds (increased)
        )
        
        # Show a message to the user
        st.success("WhatsApp message initiated! If it doesn't send automatically, please click the send button in the WhatsApp window.")
        
        # Wait for the message to be sent (adjust wait time as needed)
        time.sleep(10)
        
        debug_print("WhatsApp message operation completed")
        return True
    except Exception as e:
        debug_print(f"Error sending WhatsApp message: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error(f"Error sending WhatsApp message: {str(e)}")
        return False

def send_youtube_via_whatsapp(phone_number, video_urls, greeting_text, thanks_text):
    """
    Sends YouTube links via WhatsApp using pywhatkit
    
    Parameters:
    - phone_number: Recipient's phone number
    - video_urls: List of YouTube video URLs
    - greeting_text: Greeting message
    - thanks_text: Thank you message
    
    Returns:
    - Boolean indicating success
    """
    try:
        debug_print(f"Preparing to send YouTube links via WhatsApp to: {phone_number}")
        
        # Format the message with all video links
        video_message = f"{greeting_text}\n\n"
        for video_url in video_urls:
            video_message += f"{video_url}\n"
        video_message += f"\n{thanks_text}"
        
        # Send the message using our helper function
        return send_whatsapp_message(phone_number, video_message)
    except Exception as e:
        debug_print(f"Error sending YouTube links: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error(f"Error sending YouTube links: {str(e)}")
        return False

# Alternative method: Send message instantly with improved parameters
def send_instant_message(phone_number, message):
    try:
        debug_print(f"Preparing to send instant WhatsApp message to: {phone_number}")
        
        # Clean the phone number
        clean_number = ''.join(filter(str.isdigit, phone_number))
        if not clean_number.startswith('91') and len(clean_number) < 12:
            clean_number = '91' + clean_number
        
        # Display a message to the user
        st.info("Opening WhatsApp Web to send your message instantly. Please wait and don't interact with the browser.")
        
        # Send message instantly with improved parameters
        # - wait_time: increased to 20 seconds
        # - tab_close: set to False to keep the tab open for manual interaction if needed
        pwk.sendwhatmsg_instantly(
            f"+{clean_number}", 
            message, 
            20,  # wait_time (increased)
            False  # tab_close (set to False to keep open)
        )
        
        # Show a message to the user
        st.success("Message ready to send! If it doesn't send automatically, please manually click the send button in the WhatsApp window.")
        
        # Wait for user to potentially interact with the WhatsApp window
        time.sleep(15)
        
        debug_print("Instant message operation completed")
        return True
    except Exception as e:
        debug_print(f"Error sending instant message: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error(f"Error sending WhatsApp message: {str(e)}")
        return False

#-----------------------------------------------------------------------------------
# Phone Number Validation & Recognition
#-----------------------------------------------------------------------------------

def validate_phone_number(phone_input):
    """
    Validate a phone number and format it properly
    
    Parameters:
    - phone_input: Raw phone number input
    
    Returns:
    - Cleaned phone number or None if invalid
    """
    try:
        debug_print(f"Validating phone number: {phone_input}")
        
        # Remove all non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_input))
        debug_print(f"Cleaned number (digits only): {clean_number}")
        
        # If it's a very short number (like 495350), it might be missing digits
        # Accept it anyway but add warning
        if len(clean_number) >= 6 and len(clean_number) < 10:
            debug_print(f"Short number detected: {clean_number}, but accepting it")
            # For short numbers, add a warning but still accept
            st.warning(f"The number {clean_number} seems short. Please confirm it's correct.")
            
            # Ensure country code (India)
            formatted_number = "91" + clean_number
            debug_print(f"Formatted with country code: {formatted_number}")
            return formatted_number
            
        # Normal validation for standard numbers
        elif len(clean_number) >= 10 and len(clean_number) <= 15:
            # Format the number with country code if needed
            if not (clean_number.startswith('91') or clean_number.startswith('+91')) and len(clean_number) == 10:
                # Add India country code by default for 10-digit numbers
                formatted_number = "91" + clean_number
            else:
                # Keep as is but ensure no + sign
                formatted_number = clean_number.replace('+', '')
                
            debug_print(f"Valid number formatted: {formatted_number}")
            return formatted_number
        else:
            debug_print(f"Invalid number length: {len(clean_number)} digits")
            return None
    except Exception as e:
        debug_print(f"Phone validation error: {e}", "error")
        return None

def safe_listen_for_speech_numbers(language_code="en", timeout=10):
    """
    Enhanced version that's specialized for recognizing phone numbers
    
    Parameters:
    - language_code: Language code for recognition
    - timeout: Maximum listening time in seconds
    
    Returns:
    - Recognized text with preference for number format
    """
    try:
        debug_print(f"Starting speech recognition for phone number in language: {language_code}")
        recognition_language = {
            "en": "en-US", 
            "hi": "hi-IN", 
            "mr": "mr-IN"
        }.get(language_code, "en-US")
        
        debug_print(f"Using recognition language: {recognition_language}")
        
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                st.write("Listening for your phone number...")
                st.spinner("Listening...")
                try:
                    debug_print("Adjusting for ambient noise")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                except Exception as e:
                    debug_print(f"Error adjusting for ambient noise: {e}", "error")
                
                try:
                    debug_print(f"Listening for speech with timeout: {timeout}")
                    audio = recognizer.listen(source, timeout=timeout)
                    st.write("Processing speech...")
                    
                    # Try to recognize as phone number format
                    try:
                        debug_print("Recognizing speech with Google (preferring numbers)")
                        text = recognizer.recognize_google(audio, language=recognition_language)
                        debug_print(f"Speech recognized: {text}")
                        
                        # Extract numbers from the text
                        numbers_only = ''.join(filter(str.isdigit, text))
                        if numbers_only:
                            debug_print(f"Extracted digits: {numbers_only}")
                            # If we have digits, return them directly
                            return numbers_only
                        else:
                            return text
                    except sr.UnknownValueError:
                        debug_print("Could not understand audio", "warning")
                        st.warning("Sorry, I couldn't understand that. Please try typing your number.")
                        return None
                    except sr.RequestError as e:
                        debug_print(f"Speech recognition service error: {e}", "error")
                        st.error("Speech recognition service unavailable.")
                        return None
                except Exception as e:
                    debug_print(f"Error listening: {e}", "error")
                    return None
        except Exception as e:
            debug_print(f"Microphone error: {e}", "error")
            st.error("Could not access microphone. Please check your microphone connection and permissions.")
            return None
    except Exception as e:
        debug_print(f"Speech recognition setup error: {e}", "error")
        st.error("Speech recognition failed to initialize.")
        return None

#-----------------------------------------------------------------------------------
# Voice Agent Functions - With Enhanced Error Handling
#-----------------------------------------------------------------------------------

def safe_listen_for_speech(language_code="en", timeout=5):
    """
    Safely capture speech with robust error handling
    
    Parameters:
    - language_code: Language code for recognition
    - timeout: Maximum listening time in seconds
    
    Returns:
    - Recognized text or None
    """
    try:
        debug_print(f"Starting speech recognition in language: {language_code}")
        recognition_language = {
            "en": "en-US", 
            "hi": "hi-IN", 
            "mr": "mr-IN"
        }.get(language_code, "en-US")
        
        debug_print(f"Using recognition language: {recognition_language}")
        
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                st.write("Listening...")
                st.spinner("Listening...")
                try:
                    debug_print("Adjusting for ambient noise")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                except Exception as e:
                    debug_print(f"Error adjusting for ambient noise: {e}", "error")
                    debug_print(f"Trace: {traceback.format_exc()}", "error")
                
                try:
                    debug_print(f"Listening for speech with timeout: {timeout}")
                    audio = recognizer.listen(source, timeout=timeout)
                    st.write("Processing speech...")
                    
                    try:
                        debug_print("Recognizing speech with Google")
                        text = recognizer.recognize_google(audio, language=recognition_language)
                        debug_print(f"Speech recognized: {text}")
                        return text
                    except sr.UnknownValueError:
                        debug_print("Could not understand audio", "warning")
                        st.warning("Sorry, I couldn't understand that.")
                        return None
                    except sr.RequestError as e:
                        debug_print(f"Speech recognition service error: {e}", "error")
                        st.error("Speech recognition service unavailable.")
                        return None
                except Exception as e:
                    debug_print(f"Error listening: {e}", "error")
                    debug_print(f"Trace: {traceback.format_exc()}", "error")
                    return None
        except Exception as e:
            debug_print(f"Microphone error: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            st.error("Could not access microphone. Please check your microphone connection and permissions.")
            return None
    except Exception as e:
        debug_print(f"Speech recognition setup error: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error("Speech recognition failed to initialize.")
        return None

def text_to_speech(text, language_code="en"):
    """
    Converts text to speech and plays it with robust error handling
    
    Parameters:
    - text: Text to convert to speech
    - language_code: Language code (en, hi, mr)
    """
    debug_print(f"Converting to speech: '{text[:50]}...' in language: {language_code}")
    
    try:
        # Map language codes to gTTS language
        tts_language = {
            "en": "en",
            "hi": "hi",
            "mr": "mr"
        }.get(language_code, "en")
        
        debug_print(f"Using TTS language: {tts_language}")
        
        # Create a temporary file for the audio
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_filename = fp.name
                debug_print(f"Created temp file: {temp_filename}")
        except Exception as e:
            debug_print(f"Error creating temp file: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            st.error("Could not create temporary audio file.")
            return
        
        # Generate speech
        try:
            debug_print("Generating speech with gTTS")
            tts = gTTS(text=text, lang=tts_language, slow=False)
            tts.save(temp_filename)
            debug_print("Speech saved to temp file")
        except Exception as e:
            debug_print(f"Error generating speech: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            try:
                os.unlink(temp_filename)  # Clean up temp file
            except:
                pass
            st.error("Could not generate speech. Text-to-speech service unavailable.")
            return
        
        # Play the audio
        try:
            debug_print("Initializing pygame mixer")
            pygame.mixer.init()
            debug_print("Loading audio file")
            pygame.mixer.music.load(temp_filename)
            debug_print("Playing audio")
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            debug_print("Waiting for audio to finish")
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            debug_print("Audio playback complete")
        except Exception as e:
            debug_print(f"Error playing audio: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            st.error("Could not play audio. Check your audio settings.")
        
        # Clean up
        try:
            debug_print("Cleaning up resources")
            pygame.mixer.quit()
            os.unlink(temp_filename)
            debug_print("Resources cleaned up successfully")
        except Exception as e:
            debug_print(f"Error cleaning up: {e}", "warning")
    
    except Exception as e:
        debug_print(f"Text-to-speech error: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error("Text-to-speech failed.")

def play_video_by_voice(video_url, language_code="en"):
    """
    Asks if user wants to play a video and handles playback with error handling
    
    Parameters:
    - video_url: URL of the video to play
    - language_code: Language code (en, hi, mr)
    
    Returns:
    - Boolean indicating if video was played
    """
    debug_print(f"Asking to play video: {video_url} in language: {language_code}")
    
    try:
        play_prompt = {
            "en": "Would you like me to play this video? Say yes or no.",
            "hi": "क्या आप चाहेंगे कि मैं यह वीडियो चलाऊं? हां या ना कहें।",
            "mr": "तुम्हाला हा व्हिडिओ प्ले करायचा आहे का? होय किंवा नाही म्हणा."
        }.get(language_code, "Would you like me to play this video? Say yes or no.")
        
        debug_print(f"Play prompt: {play_prompt}")
        
        try:
            text_to_speech(play_prompt, language_code)
        except Exception as e:
            debug_print(f"Error in play prompt speech: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
        
        debug_print("Listening for response")
        response = safe_listen_for_speech(language_code)
        debug_print(f"Received response: {response}")
        
        if response and any(word in response.lower() for word in ["yes", "हां", "होय", "play", "ok", "sure", "yeah"]):
            debug_print("User confirmed video playback")
            st.video(video_url)
            return True
        else:
            debug_print("User declined video playback or response not understood")
        
        return False
    except Exception as e:
        debug_print(f"Error in video playback: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error("Could not play video.")
        return False

#-----------------------------------------------------------------------------------
# Natural Language Processing Functions - With Enhanced Error Handling
#-----------------------------------------------------------------------------------

def translate_query_to_english(query, source_language=None):
    """
    Detects if the query is not in English and translates it to English.
    Enhanced with robust error handling.
    
    Parameters:
    - query: User query string
    - source_language: Optional language code (e.g., 'hi' for Hindi, 'mr' for Marathi)
    
    Returns:
    - Translated query in English
    - Original language detected
    """
    debug_print(f"Translating query: '{query}' from language: {source_language}")
    
    try:
        # Check if query is None or empty
        if not query or query.strip() == "":
            debug_print("Query is empty, returning empty string and default language", "warning")
            return "", "en"
        
        # Check if query contains non-Latin characters
        has_non_latin = any(ord(char) > 127 for char in query)
        debug_print(f"Query has non-Latin characters: {has_non_latin}")
        
        if not has_non_latin:
            debug_print("Query appears to be in Latin script, returning as is")
            return query, "en"  # Return as is if likely English
        
        # If source language is explicitly provided and not English
        if source_language and source_language != "en":
            debug_print(f"Using provided source language: {source_language}")
            
            # Attempt to use OpenAI for translation
            try:
                debug_print("Attempting translation with OpenAI")
                messages = [
                    {"role": "system", "content": "You are a translator that converts non-English queries to English. Return ONLY the translated text, nothing else."},
                    {"role": "user", "content": f"Translate this query to English: '{query}'"}
                ]
                
                if source_language:
                    language_names = {"hi": "Hindi", "mr": "Marathi"}
                    lang_name = language_names.get(source_language, source_language)
                    debug_print(f"Adding source language to prompt: {lang_name}")
                    messages[0]["content"] += f" The source language is {lang_name}."
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=100,
                    temperature=0.3
                )
                
                translated_query = response['choices'][0]['message']['content'].strip()
                debug_print(f"Translated query: '{translated_query}'")
                return translated_query, source_language
            except Exception as e:
                debug_print(f"OpenAI translation error: {e}", "error")
                debug_print(f"Trace: {traceback.format_exc()}", "error")
                st.warning(f"Translation service error. Processing original query.")
                return query, source_language
        
        # If no translation needed or possible
        debug_print("No translation needed or source language not specified")
        return query, "en"
        
    except Exception as e:
        debug_print(f"Translation error: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error(f"Translation failed. Using original query.")
        # Return a safe default in case of any error
        return query, "en"

def extract_keywords_from_query(natural_query, language="en"):
    """
    Extract technical keywords from a query, supporting multiple languages.
    Enhanced with robust error handling.
    
    Parameters:
    - natural_query: The user's query
    - language: Language code (en, hi, mr)
    
    Returns:
    - List of keywords
    """
    debug_print(f"Extracting keywords from query: '{natural_query}' in language: {language}")
    
    try:
        # Check if query is None or empty
        if not natural_query or natural_query.strip() == "":
            debug_print("Query is empty, returning default keywords", "warning")
            return ["inverter", "solar", "enertech"]
        
        # Translate query to English if not already in English
        if language != "en":
            try:
                debug_print(f"Translating query from {language} to English")
                english_query, _ = translate_query_to_english(natural_query, language)
                debug_print(f"Translated query: '{english_query}'")
            except Exception as e:
                debug_print(f"Translation for keyword extraction failed: {e}", "error")
                english_query = natural_query
        else:
            english_query = natural_query
            
        # Try to extract keywords using OpenAI
        try:
            debug_print("Extracting keywords with OpenAI")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical assistant for Enertech solar hybrid inverters. Extract 3-5 technical keywords from the user's query that would help match it to relevant tutorial videos."},
                    {"role": "user", "content": f"Extract the main technical keywords from this query about solar inverters: '{english_query}'. Return only the keywords separated by commas, no explanation."}
                ],
                max_tokens=50,
                temperature=0.3
            )
            keywords = response['choices'][0]['message']['content'].strip()
            debug_print(f"Extracted keywords: {keywords}")
            
            # Split the keywords and clean them
            keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
            
            # Check if we got valid keywords
            if not keyword_list:
                debug_print("No valid keywords returned from OpenAI, using fallback", "warning")
                raise ValueError("No valid keywords returned")
                
            return keyword_list
        except Exception as e:
            debug_print(f"OpenAI keyword extraction error: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            
            # Fallback method if OpenAI fails
            debug_print("Using fallback keyword extraction")
            words = re.findall(r'\b\w+\b', english_query)
            keywords = [word.lower() for word in words if len(word) > 3 and word.lower() not in {
                'help', 'what', 'with', 'that', 'this', 'have', 'from', 'about', 'there',
                'their', 'where', 'when', 'how', 'why', 'who', 'will', 'would', 'could',
                'should', 'can', 'may', 'might', 'must', 'shall', 'are', 'were', 'was',
                'been', 'being', 'have', 'has', 'had', 'does', 'did', 'doing', 'done'
            }]
            
            # If still no keywords, use defaults
            if not keywords:
                debug_print("Fallback extraction yielded no keywords, using defaults", "warning")
                keywords = ["inverter", "solar", "enertech"]
                
            debug_print(f"Fallback keywords: {keywords}")
            return keywords
    except Exception as e:
        debug_print(f"Keyword extraction error: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        # Return basic fallback keywords if everything fails
        return ["inverter", "solar", "enertech"]

def convert_to_professional_query(natural_query):
    """
    Convert natural language to title-style format matching video titles.
    Enhanced with robust error handling.
    
    Parameters:
    - natural_query: The user's natural language query
    
    Returns:
    - Formatted query in title style
    """
    debug_print(f"Converting query to professional format: '{natural_query}'")
    
    try:
        # Check if query is None or empty
        if not natural_query or natural_query.strip() == "":
            debug_print("Query is empty, returning default title", "warning")
            return "EnerTech Solar Hybrid Inverter Troubleshooting"
        
        # Try using OpenAI for formatting
        try:
            debug_print("Using OpenAI for query formatting")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a technical formatter for Enertech solar hybrid inverters. 
                    Convert user queries into instructional title format that matches these examples:
                    - "How to Fix Overload Fault in REeFI Solar Hybrid Inverter | Error Code 409"
                    - "How to Change REeFI Solar Hybrid Inverter Mode | Inverter Mode Setup"
                    - "How to Set Batteryless Mode in EnerTech Solar Hybrid Inverter"
                    - "Troubleshooting CAN Bus Errors or Communication Error"
                    
                    Use the "How to [Action] [Product] | [Additional Info]" format whenever possible.
                    Capitalize important words like a title would.
                    Include technical terms like REeFI, EnerTech, Solar Hybrid Inverter where appropriate.
                    """},
                    {"role": "user", "content": f"Convert this user query into a technical instructional title format: '{natural_query}'"}
                ],
                max_tokens=60,
                temperature=0.3
            )
            title_style_query = response['choices'][0]['message']['content'].strip()
            debug_print(f"Formatted query: '{title_style_query}'")
            return title_style_query
        except Exception as e:
            debug_print(f"OpenAI formatting error: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            
            # Fallback formatting if API fails
            debug_print("Using fallback query formatting")
            words = natural_query.split()
            
            # Default format: "How to [Action] [Product]"
            if len(words) > 2:
                if natural_query.lower().startswith("how to"):
                    formatted = natural_query.capitalize()
                else:
                    formatted = f"How to {natural_query.capitalize()}"
            else:
                formatted = f"EnerTech Solar Inverter {natural_query.capitalize()}"
                
            if "inverter" not in formatted.lower():
                formatted += " in Solar Hybrid Inverter"
                
            debug_print(f"Fallback formatted query: '{formatted}'")
            return formatted
    except Exception as e:
        debug_print(f"Query formatting error: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        # Return safe default if everything fails
        return f"How to Fix {natural_query.capitalize()} in EnerTech Solar Inverter"

def find_relevant_youtube_videos(query, top_n=3):
    """
    Find the most relevant YouTube videos based on the user query, with enhanced error handling.
    
    Parameters:
    - query: User query string
    - top_n: Number of top videos to return
    
    Returns:
    - List of relevant video objects
    """
    debug_print(f"Finding relevant videos for query: '{query}'")
    
    try:
        # Check for empty query
        if not query or query.strip() == "":
            debug_print("Empty query, returning default videos", "warning")
            # Return a selection of general videos
            return youtube_videos[:min(top_n, len(youtube_videos))]
        
        # Prepare for matching
        query_lower = query.lower()
        debug_print(f"Lowercase query: '{query_lower}'")
        
        # Extract key terms from query (terms with 3+ characters)
        query_terms = [term for term in query_lower.split() if len(term) > 2]
        debug_print(f"Query terms: {query_terms}")
        
        if not query_terms:
            debug_print("No significant query terms found, using full query", "warning")
            query_terms = [query_lower]
        
        # Score videos using a balanced approach across all metadata
        scored_videos = []
        
        for i, video in enumerate(youtube_videos):
            try:
                # Initialize component scores
                title_score = 0
                description_score = 0
                keyword_score = 0
                category_score = 0
                
                # Get video metadata
                title_lower = video["title"].lower()
                description_lower = video["description"].lower()
                video_keywords = [k.lower() for k in video["keywords"]]
                category = video.get("category", "").lower()
                
                debug_print(f"Scoring video {i+1}: '{video['title']}'")
                
                # 1. TITLE MATCHING (33% weight)
                for term in query_terms:
                    if term in title_lower:
                        # Exact match in title
                        title_score += 1
                        debug_print(f"  Term '{term}' found in title: +1")
                        
                        # Bonus for technical terms and error codes
                        if term.isdigit() and len(term) >= 3:
                            title_score += 2  # Error code match
                            debug_print(f"  Term '{term}' is error code: +2")
                        elif term in ["inverter", "solar", "hybrid", "enertech", "reefi", "sunmagic", "enertron"]:
                            title_score += 0.5  # Product name match
                            debug_print(f"  Term '{term}' is product name: +0.5")
                
                # 2. DESCRIPTION MATCHING (33% weight)
                for term in query_terms:
                    if term in description_lower:
                        description_score += 0.5
                        debug_print(f"  Term '{term}' found in description: +0.5")
                        
                        # Check for phrases (2+ consecutive terms)
                        if len(query_terms) > 1:
                            for i in range(len(query_terms) - 1):
                                if i < len(query_terms) - 1:
                                    phrase = f"{query_terms[i]} {query_terms[i+1]}"
                                    if phrase in description_lower:
                                        description_score += 1  # Bonus for phrase match
                                        debug_print(f"  Phrase '{phrase}' found in description: +1")
                
                # 3. KEYWORD MATCHING (33% weight)
                matching_keywords = 0
                for term in query_terms:
                    for keyword in video_keywords:
                        if term in keyword:
                            matching_keywords += 1
                            debug_print(f"  Term '{term}' matches keyword '{keyword}'")
                            break  # Count each query term only once
                
                # Normalize keyword score by number of query terms
                if query_terms:
                    keyword_score = min(3, matching_keywords) / min(3, len(query_terms)) * 3
                    debug_print(f"  Keyword score: {keyword_score:.2f}")
                
                # 4. CATEGORY MATCHING (bonus)
                if any(term in query_lower for term in ["problem", "error", "fault", "not working", "fix", "issue", "blank"]):
                    if category == "troubleshooting":
                        category_score = 1
                        debug_print("  Category bonus: Troubleshooting +1")
                elif any(term in query_lower for term in ["setup", "install", "configure", "setting", "mode"]):
                    if category == "setup" or category == "installation":
                        category_score = 1
                        debug_print("  Category bonus: Setup/Installation +1")
                elif any(term in query_lower for term in ["emergency", "safety", "switch", "shutdown"]):
                    if category == "safety":
                        category_score = 1
                        debug_print("  Category bonus: Safety +1")
                
                # 5. SPECIAL CASE HANDLING
                special_case_score = 0
                
                # Blank screen issue
                if ("blank" in query_lower or "black" in query_lower) and ("screen" in query_lower or "display" in query_lower):
                    # Check if video mentions display issues in any metadata
                    if any(term in title_lower for term in ["mode", "setting", "troubleshoot"]):
                        special_case_score += 2
                        debug_print("  Special case: Blank screen title match +2")
                    if any(term in " ".join(video_keywords) for term in ["troubleshooting", "reset", "restart"]):
                        special_case_score += 1
                        debug_print("  Special case: Blank screen keyword match +1")
                    if any(term in description_lower for term in ["display", "screen", "restart", "reboot"]):
                        special_case_score += 1
                        debug_print("  Special case: Blank screen description match +1")
                
                # Battery relay errors
                if "relay" in query_lower and "battery" in query_lower:
                    if "relay" in title_lower and "battery" in title_lower:
                        special_case_score += 3
                        debug_print("  Special case: Battery relay match +3")
                        
                # Grid export setting
                if "grid" in query_lower and "export" in query_lower:
                    if "grid export" in title_lower:
                        special_case_score += 3
                        debug_print("  Special case: Grid export match +3")
                        
                # Batteryless mode
                if "batteryless" in query_lower or ("without" in query_lower and "battery" in query_lower):
                    if "batteryless" in title_lower or "without battery" in title_lower:
                        special_case_score += 3
                        debug_print("  Special case: Batteryless match +3")
                
                # Calculate final combined score with balanced weighting
                combined_score = (
                    (title_score * 0.33) + 
                    (description_score * 0.33) + 
                    (keyword_score * 0.33) + 
                    category_score +
                    special_case_score
                )
                
                debug_print(f"  Final score: {combined_score:.2f}")
                scored_videos.append((combined_score, video))
                
            except Exception as e:
                debug_print(f"Error scoring video {i}: {e}", "error")
                # Continue with next video
        
        # Sort videos by combined score in descending order
        scored_videos.sort(reverse=True, key=lambda x: x[0])
        
        # Filter based on a minimum threshold
        relevant = [video for score, video in scored_videos if score > 0.5]
        debug_print(f"Found {len(relevant)} videos above threshold")
        
        # If we have no videos above threshold but have scored videos, return at least one
        if not relevant and scored_videos:
            debug_print("No videos above threshold, returning highest scored video")
            relevant = [scored_videos[0][1]]  # Return the highest scored video even if below threshold
        
        # Return top results
        results = relevant[:top_n]
        debug_print(f"Returning {len(results)} videos")
        return results
    except Exception as e:
        debug_print(f"Error finding videos: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        # Return a safe default in case of errors
        return youtube_videos[:min(top_n, len(youtube_videos))]

def safe_get_videos(query, top_n=3):
    """
    Safely find relevant videos with proper error handling
    
    Parameters:
    - query: Formatted query string
    - top_n: Number of videos to return
    
    Returns:
    - List of relevant videos (or empty list if error)
    """
    try:
        return find_relevant_youtube_videos(query, top_n)
    except Exception as e:
        debug_print(f"Error finding videos: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        return []

def handle_query_safely(query, language_code):
    """
    Process a user query with robust error handling
    
    Parameters:
    - query: The raw user query
    - language_code: Language code (en, hi, mr)
    
    Returns:
    - english_query: Translated query
    - keywords: Extracted keywords
    - formal_query: Professional formatted query
    """
    try:
        debug_print(f"Safely handling query: '{query}' in language: {language_code}")
        
        # Translate if needed (with fallback)
        try:
            debug_print("Step 1: Translating query")
            english_query, detected_lang = translate_query_to_english(query, language_code)
            debug_print(f"Translation result: '{english_query}', detected language: {detected_lang}")
        except Exception as e:
            debug_print(f"Translation error: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            english_query, detected_lang = query, language_code
            debug_print("Using original query due to translation error")
            
        # Extract keywords (with fallback)
        try:
            debug_print("Step 2: Extracting keywords")
            keywords = extract_keywords_from_query(english_query)
            debug_print(f"Extracted keywords: {keywords}")
        except Exception as e:
            debug_print(f"Keyword extraction error: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            keywords = ["inverter", "solar", "enertech"]
            debug_print("Using default keywords due to extraction error")
            
        # Format query (with fallback)
        try:
            debug_print("Step 3: Formatting query")
            formal_query = convert_to_professional_query(english_query)
            debug_print(f"Formatted query: '{formal_query}'")
        except Exception as e:
            debug_print(f"Query formatting error: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            formal_query = f"How to Fix {english_query.capitalize()}"
            debug_print("Using simple format due to formatting error")
            
        return english_query, keywords, formal_query
    except Exception as e:
        debug_print(f"Query processing error: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        # Ultimate fallback
        return query, ["inverter", "solar", "enertech"], f"How to Fix {query.capitalize()}"

#-----------------------------------------------------------------------------------
# Call Flow Functions
#-----------------------------------------------------------------------------------

def display_call_interface():
    """Display the call interface UI"""
    st.markdown("""
    <style>
    .call-button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 50px;
    }
    .hang-button {
        background-color: #f44336;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 50px;
    }
    .call-status {
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-ringing {
        background-color: #ffe0b2;
        color: #e65100;
    }
    .status-connected {
        background-color: #c8e6c9;
        color: #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.get('call_started', False):
            if st.button("📞 Start Call", key="start_call", help="Start a call with Enertech Support", 
                       use_container_width=True, type="primary"):
                st.session_state.call_started = True
                st.session_state.call_status = "ringing"
                st.session_state.call_step = 0  # Initialize step counter
                # Reset all greeting flags
                st.session_state.greeting_played_step_1 = False
                st.session_state.greeting_played_step_2 = False
                st.session_state.greeting_played_step_3 = False
                st.rerun()
    
    with col2:
        if st.session_state.get('call_started', False):
            if st.button("🔴 Hang Up", key="hang_up", help="End the call", 
                       use_container_width=True, type="primary"):
                # End the call and process final steps
                st.session_state.call_started = False
                st.session_state.call_status = "completed"
                
                # Send videos automatically if we have query results
                if st.session_state.get('video_links', []):
                    st.session_state.auto_send_videos = True
                
                st.rerun()

    # Display call status
    if st.session_state.get('call_status') == "ringing":
        st.markdown('<div class="call-status status-ringing">📞 Calling Enertech Support...</div>', unsafe_allow_html=True)
    elif st.session_state.get('call_status') == "connected":
        st.markdown('<div class="call-status status-connected">📞 Connected to Enertech Support</div>', unsafe_allow_html=True)

#-----------------------------------------------------------------------------------
# Main Application
#-----------------------------------------------------------------------------------

def main():
    # Enable or disable debug mode
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    
    # Debug mode toggle
    if st.sidebar.checkbox("Debug Mode", value=st.session_state.debug_mode):
        st.session_state.debug_mode = True
        debug_print("Debug mode enabled")
    else:
        st.session_state.debug_mode = False
    
    st.title("Enertech Voice Support Assistant")
    
    # Sidebar for user input
    st.sidebar.title("Support Assistant")
    st.sidebar.subheader("Language Selection")
    language = st.sidebar.selectbox("Choose Language", ("English", "Hindi", "Marathi"))
    
    # Map language selection to language code
    language_code = {"English": "en", "Hindi": "hi", "Marathi": "mr"}.get(language, "en")
    debug_print(f"Selected language: {language} (code: {language_code})")

    st.sidebar.subheader("📺 YouTube Help Center")
    yt_query = st.sidebar.text_input("Search video tutorials")

    # Initialize session state variables
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        debug_print("Initialized messages list")
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
        debug_print("Initialized current_query")
    if 'phone_number' not in st.session_state:
        st.session_state.phone_number = ""
        debug_print("Initialized phone_number")
    if 'temp_phone_number' not in st.session_state:
        st.session_state.temp_phone_number = ""
        debug_print("Initialized temp_phone_number")
    if 'call_started' not in st.session_state:
        st.session_state.call_started = False
        debug_print("Initialized call_started")
    if 'call_status' not in st.session_state:
        st.session_state.call_status = "idle"
        debug_print("Initialized call_status")
    if 'call_step' not in st.session_state:
        st.session_state.call_step = 0
        debug_print("Initialized call_step")
    if 'video_links' not in st.session_state:
        st.session_state.video_links = []
        debug_print("Initialized video_links")
    if 'greeting_played_step_1' not in st.session_state:
        st.session_state.greeting_played_step_1 = False
        debug_print("Initialized greeting_played_step_1")
    if 'greeting_played_step_2' not in st.session_state:
        st.session_state.greeting_played_step_2 = False
        debug_print("Initialized greeting_played_step_2")
    if 'greeting_played_step_3' not in st.session_state:
        st.session_state.greeting_played_step_3 = False
        debug_print("Initialized greeting_played_step_3")
        
    # Display the call interface
    display_call_interface()
        
    # Handle call flow
    if st.session_state.get('call_started', False):
        debug_print(f"Call is active, step: {st.session_state.call_step}")
        
        # STEP 0: Ringing and connecting
        if st.session_state.call_step == 0:
            debug_print("Call step 0: Ringing and connecting")
            
            # Display ringing animation/sound
            try:
                play_ringing_sound()
                
                # Update to connected status
                st.session_state.call_status = "connected"
                play_connected_sound()
                
                # Progress to next step
                st.session_state.call_step = 1
                st.session_state.greeting_played_step_1 = False  # Ensure greeting will be played in step 1
                st.rerun()
            except Exception as e:
                debug_print(f"Error in call connection step: {e}", "error")
                debug_print(f"Trace: {traceback.format_exc()}", "error")
                # Fallback to next step even if sound fails
                st.session_state.call_status = "connected"
                st.session_state.call_step = 1
                st.session_state.greeting_played_step_1 = False  # Ensure greeting will be played in step 1
                st.rerun()
        
        # STEP 1: Greeting and asking for phone number
        elif st.session_state.call_step == 1:
            debug_print("Call step 1: Greeting and asking for phone number")
            
            try:
                # Greeting message - only play once
                if not st.session_state.greeting_played_step_1:
                    greeting_text = {
                        "en": f"Welcome to Enertech Support! I'm here to help you with your solar inverter. First, please tell me your WhatsApp number so I can send you helpful videos later.",
                        "hi": f"एनरटेक सपोर्ट में आपका स्वागत है! मैं आपके सोलर इनवर्टर के साथ आपकी मदद करने के लिए यहां हूं। सबसे पहले, कृपया मुझे अपना व्हाट्सएप नंबर बताएं ताकि मैं आपको बाद में सहायक वीडियो भेज सकूं।",
                        "mr": f"एनरटेक सपोर्टमध्ये आपले स्वागत आहे! मी तुमच्या सोलर इन्व्हर्टरसाठी मदत करण्यासाठी येथे आहे. प्रथम, कृपया मला तुमचा व्हॉट्सअॅप नंबर सांगा जेणेकरून मी तुम्हाला नंतर मदतशीर व्हिडिओ पाठवू शकेन."
                    }.get(language_code, "Welcome to Enertech Support! I'm here to help you with your solar inverter. First, please tell me your WhatsApp number so I can send you helpful videos later.")
                    
                    text_to_speech(greeting_text, language_code)
                    st.session_state.greeting_played_step_1 = True
                
                # Input for WhatsApp number
                phone_prompt = {
                    "en": "Please say or type your WhatsApp number:",
                    "hi": "कृपया अपना व्हाट्सएप नंबर कहें या टाइप करें:",
                    "mr": "कृपया आपला व्हॉट्सअॅप नंबर सांगा किंवा टाइप करा:"
                }.get(language_code, "Please say or type your WhatsApp number:")
                
                # First try voice input for phone number
                st.subheader(phone_prompt)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🎤 Speak Your Number"):
                        # Use the specialized number recognition
                        number = safe_listen_for_speech_numbers(language_code, timeout=10)
                        if number:
                            # The number should already be in digit format
                            clean_number = validate_phone_number(number)
                            if clean_number:
                                # Show number for confirmation
                                st.session_state.temp_phone_number = clean_number
                                st.success(f"I heard: +{clean_number}")
                                
                                # Add confirmation step
                                confirm_text = {
                                    "en": f"Is +{clean_number} your correct WhatsApp number?",
                                    "hi": f"क्या +{clean_number} आपका सही व्हाट्सएप नंबर है?",
                                    "mr": f"+{clean_number} हा तुमचा अचूक व्हॉट्सअॅप नंबर आहे का?"
                                }.get(language_code, f"Is +{clean_number} your correct WhatsApp number?")
                                
                                text_to_speech(confirm_text, language_code)
                                
                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("✅ Yes, it's correct"):
                                        st.session_state.phone_number = clean_number
                                        st.session_state.call_step = 2
                                        st.session_state.greeting_played_step_2 = False  # Reset for next step
                                        st.rerun()
                                with col_no:
                                    if st.button("❌ No, let me type it"):
                                        st.session_state.temp_phone_number = ""
                                        st.rerun()
                            else:
                                st.warning("I couldn't convert that to a valid phone number. Please try typing it.")
                
                with col2:
                    # Also allow typed input
                    default_value = st.session_state.get('temp_phone_number', '')
                    phone_input = st.text_input("Or type your phone number:", value=default_value)
                    if phone_input:
                        # Clean the number - extract only digits
                        clean_number = validate_phone_number(phone_input)
                        if clean_number:
                            # Show confirmation button
                            st.success(f"Phone number: +{clean_number}")
                            if st.button("✅ Confirm this number"):
                                st.session_state.phone_number = clean_number
                                st.session_state.call_step = 2
                                st.session_state.greeting_played_step_2 = False  # Reset for next step
                                st.rerun()
                        else:
                            st.warning("Please enter a valid phone number (6+ digits).")
            except Exception as e:
                debug_print(f"Error in greeting step: {e}", "error")
                debug_print(f"Trace: {traceback.format_exc()}", "error")
                # Fallback to allow manual input
                st.error("There was an error. Please type your phone number manually.")
                phone_input = st.text_input("Your phone number:")
                if phone_input:
                    clean_number = validate_phone_number(phone_input)
                    if clean_number:
                        if st.button("✅ Confirm Number"):
                            st.session_state.phone_number = clean_number
                            st.session_state.call_step = 2
                            st.session_state.greeting_played_step_2 = False  # Reset for next step
                            st.rerun()
                    else:
                        st.warning("Please enter a valid phone number.")
        
        # STEP 2: Ask for the query
        elif st.session_state.call_step == 2:
            debug_print("Call step 2: Ask for the query")
            
            try:
                # Confirm phone number reception - only play once
                if not st.session_state.greeting_played_step_2:
                    confirm_text = {
                        "en": f"Thank you! I've noted your number +{st.session_state.phone_number}. Now, please tell me what issue you're facing with your EnerTech solar inverter.",
                        "hi": f"धन्यवाद! मैंने आपका नंबर +{st.session_state.phone_number} नोट कर लिया है। अब, कृपया मुझे बताएं कि आपको अपने एनरटेक सोलर इनवर्टर के साथ किस समस्या का सामना करना पड़ रहा है।",
                        "mr": f"धन्यवाद! मी तुमचा नंबर +{st.session_state.phone_number} नोंद केला आहे. आता, कृपया मला सांगा की तुम्हाला तुमच्या एनरटेक सोलर इन्व्हर्टरसह कोणत्या समस्येचा सामना करावा लागत आहे."
                    }.get(language_code, f"Thank you! I've noted your number +{st.session_state.phone_number}. Now, please tell me what issue you're facing with your EnerTech solar inverter.")
                    
                    text_to_speech(confirm_text, language_code)
                    st.session_state.greeting_played_step_2 = True
                
                # Get the user's query
                query_prompt = {
                    "en": "What problem are you experiencing with your inverter?",
                    "hi": "आपको अपने इनवर्टर के साथ क्या समस्या हो रही है?",
                    "mr": "तुम्हाला तुमच्या इन्व्हर्टरसह कोणती समस्या येत आहे?"
                }.get(language_code, "What problem are you experiencing with your inverter?")
                
                st.subheader(query_prompt)
                
                # Voice input for query
                if st.button("🎤 Describe Your Issue"):
                    query = safe_listen_for_speech(language_code, timeout=15)  # Longer timeout for detailed explanation
                    if query:
                        st.info(f"You said: {query}")
                        st.session_state.current_query = query
                        st.session_state.call_step = 3
                        st.session_state.greeting_played_step_3 = False  # Reset for next step
                        st.rerun()
                    else:
                        st.warning("I couldn't understand your issue. Please try again or type it below.")
                
                # Also allow typed input
                text_query = st.text_input("Or type your issue:")
                if text_query:
                    st.session_state.current_query = text_query
                    st.session_state.call_step = 3
                    st.session_state.greeting_played_step_3 = False  # Reset for next step
                    st.rerun()
            except Exception as e:
                debug_print(f"Error in query step: {e}", "error")
                debug_print(f"Trace: {traceback.format_exc()}", "error")
                # Fallback to allow manual input
                st.error("There was an error. Please type your issue manually.")
                text_query = st.text_input("Describe the issue you're experiencing:")
                if text_query:
                    st.session_state.current_query = text_query
                    st.session_state.call_step = 3
                    st.session_state.greeting_played_step_3 = False  # Reset for next step
                    st.rerun()
        
        # STEP 3: Process query and provide video results
        elif st.session_state.call_step == 3:
            debug_print("Call step 3: Process query and provide results")
            
            try:
                query = st.session_state.current_query
                
                # Process the query with the safe helper function
                debug_print("Handling query safely")
                english_query, keywords, formal_query = handle_query_safely(query, language_code)
                
                # Optional debug info
                with st.expander("Query Analysis (Debug)", expanded=st.session_state.debug_mode):
                    st.write(f"Original Query: {query}")
                    st.write(f"English Query: {english_query}")
                    st.write(f"Formal Query: {formal_query}")
                    st.write(f"Extracted Keywords: {', '.join(keywords)}")
                    st.write(f"Selected Language: {language} ({language_code})")

                # Safely find relevant videos
                debug_print("Finding relevant videos")
                relevant_videos = safe_get_videos(formal_query)
                debug_print(f"Found {len(relevant_videos)} relevant videos")
                
                if relevant_videos:
                    # Create response text for speech - only play once
                    if not st.session_state.greeting_played_step_3:
                        video_response = {
                            "en": f"I found {len(relevant_videos)} videos that explain how to solve your problem. Let me show them to you.",
                            "hi": f"मुझे आपकी समस्या को हल करने के लिए {len(relevant_videos)} वीडियो मिले हैं। मैं आपको उन्हें दिखाता हूं।",
                            "mr": f"मला तुमची समस्या सोडवण्यासाठी {len(relevant_videos)} व्हिडिओ सापडले आहेत. मी तुम्हाला ते दाखवतो."
                        }.get(language_code, f"I found {len(relevant_videos)} videos that explain how to solve your problem. Let me show them to you.")
                        
                        text_to_speech(video_response, language_code)
                        st.session_state.greeting_played_step_3 = True
                    
                    # Customize heading based on selected language
                    video_heading = {
                        "en": "🎥 Recommended Solution Videos:",
                        "hi": "🎥 अनुशंसित समाधान वीडियो:",
                        "mr": "🎥 शिफारस केलेले सोल्यूशन व्हिडिओ:"
                    }.get(language_code, "🎥 Recommended Solution Videos:")
                    
                    st.markdown(f"### {video_heading}")
                    
                    video_links = []
                    for i, video in enumerate(relevant_videos):
                        st.markdown(f"**{video['title']}**")
                        
                        # Display video details
                        with st.expander("Video Description", expanded=False):
                            st.write(video['description'])
                            st.write(f"**Category:** {video.get('category', 'Unknown')}")
                        
                        # Show the video directly
                        st.video(video['url'])
                        
                        video_links.append(video['url'])
                    
                    # Store video links for automatic sending when call ends
                    st.session_state.video_links = video_links
                    
                    # Add note about WhatsApp
                    whatsapp_note = {
                        "en": "When we finish the call, I'll automatically send these videos to your WhatsApp number for future reference.",
                        "hi": "जब हम कॉल समाप्त करेंगे, तो मैं भविष्य के संदर्भ के लिए इन वीडियो को स्वचालित रूप से आपके व्हाट्सएप नंबर पर भेज दूंगा।",
                        "mr": "आपण कॉल संपवल्यानंतर, मी भविष्यातील संदर्भासाठी हे व्हिडिओ आपोआप तुमच्या व्हॉट्सअॅप नंबरवर पाठवेन."
                    }.get(language_code, "When we finish the call, I'll automatically send these videos to your WhatsApp number for future reference.")
                    
                    st.info(whatsapp_note)
                    if not st.session_state.greeting_played_step_3:
                        text_to_speech(whatsapp_note, language_code)
                    
                    # Hang up prompt
                    hangup_prompt = {
                        "en": "Is there anything else I can help you with? If not, you can hang up the call when ready.",
                        "hi": "क्या कुछ और है जिसमें मैं आपकी मदद कर सकता हूं? यदि नहीं, तो आप तैयार होने पर कॉल काट सकते हैं।",
                        "mr": "मी तुम्हाला आणखी काही मदत करू शकतो का? नसल्यास, तुम्ही तयार असल्यावर कॉल हँग अप करू शकता."
                    }.get(language_code, "Is there anything else I can help you with? If not, you can hang up the call when ready.")
                    
                    if not st.session_state.greeting_played_step_3:
                        text_to_speech(hangup_prompt, language_code)
                    
                    # Move to waiting for hang up
                    st.session_state.call_step = 4
                else:
                    # No relevant videos warning
                    no_relevant_videos_text = {
                        "en": "I couldn't find any videos specifically about that issue. Would you like to try explaining your problem differently?",
                        "hi": "मुझे इस समस्या के बारे में कोई विशेष वीडियो नहीं मिला। क्या आप अपनी समस्या को अलग तरीके से समझाना चाहेंगे?",
                        "mr": "मला त्या समस्येबद्दल विशेषतः कोणतेही व्हिडिओ सापडले नाहीत. तुम्ही तुमची समस्या वेगळ्या प्रकारे स्पष्ट करू इच्छिता का?"
                    }.get(language_code, "I couldn't find any videos specifically about that issue. Would you like to try explaining your problem differently?")
                    
                    text_to_speech(no_relevant_videos_text, language_code)
                    st.warning(no_relevant_videos_text)
                    
                    # Option to try again
                    if st.button("🎤 Try Explaining Again"):
                        st.session_state.current_query = ""
                        st.session_state.call_step = 2
                        st.session_state.greeting_played_step_2 = False  # Reset for next step
                        st.rerun()
            except Exception as e:
                debug_print(f"Error processing query: {e}", "error")
                debug_print(f"Trace: {traceback.format_exc()}", "error")
                st.error(f"Error processing your query: {str(e)}")
        
        # STEP 4: Waiting for user to hang up
        elif st.session_state.call_step == 4:
            debug_print("Call step 4: Waiting for hang up")
            
            # Display hang up reminder
            st.info("You can hang up the call when you're ready. The videos will be sent to your WhatsApp.")
            
            # Any additional actions here while waiting for hang up
    
    # Handle call completion - Auto-send WhatsApp videos
    if not st.session_state.get('call_started', False) and st.session_state.get('auto_send_videos', False) and st.session_state.get('video_links', []):
        debug_print("Call ended, sending WhatsApp videos automatically")
        
        try:
            # Define custom messages based on language
            greeting_text = {
                "en": "Hello from Enertech Support! Here are the videos that will help solve your problem:",
                "hi": "एनरटेक सपोर्ट से नमस्ते! ये वीडियो आपकी समस्या को हल करने में मदद करेंगे:",
                "mr": "एनरटेक सपोर्टकडून नमस्कार! तुमची समस्या सोडवण्यात मदत करणारे हे व्हिडिओ आहेत:"
            }.get(language_code, "Hello from Enertech Support! Here are the videos that will help solve your problem:")
            
            thanks_text = {
                "en": "Thank you for contacting Enertech Support! Feel free to call again if you have any other questions.",
                "hi": "एनरटेक सपोर्ट से संपर्क करने के लिए धन्यवाद! यदि आपके पास कोई अन्य प्रश्न हैं तो बेझिझक फिर से कॉल करें।",
                "mr": "एनरटेक सपोर्टशी संपर्क साधल्याबद्दल धन्यवाद! तुम्हाला अजून काही प्रश्न असल्यास पुन्हा कॉल करण्यास मोकळे असा."
            }.get(language_code, "Thank you for contacting Enertech Support! Feel free to call again if you have any other questions.")
            
            # Show sending status
            with st.spinner("Sending videos to your WhatsApp..."):
                st.info("I'll open WhatsApp Web to send the videos. You may need to click the send button if it doesn't send automatically.")
                success = send_youtube_via_whatsapp(
                    st.session_state.phone_number, 
                    st.session_state.video_links,
                    greeting_text,
                    thanks_text
                )
                
                if success:
                    st.success("WhatsApp message with videos has been prepared. If it didn't send automatically, please click the send button in the WhatsApp window.")
                else:
                    # Try alternative method
                    st.warning("Trying alternative method to send the videos...")
                    
                    video_message = f"{greeting_text}\n\n"
                    for video_url in st.session_state.video_links:
                        video_message += f"{video_url}\n"
                    video_message += f"\n{thanks_text}"
                    
                    if send_instant_message(st.session_state.phone_number, video_message):
                        st.success("WhatsApp message with videos has been prepared using an alternative method. Please check the WhatsApp window and click send if needed.")
                    else:
                        st.error("Could not send videos to WhatsApp. Here are the links you can use:")
                        for link in st.session_state.video_links:
                            st.code(link)
        except Exception as e:
            debug_print(f"Error sending WhatsApp after call: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            st.error("Error sending WhatsApp messages. Please copy the video links manually:")
            for link in st.session_state.video_links:
                st.code(link)
        
        # Reset auto-send flag
        st.session_state.auto_send_videos = False

    # Optional: Sidebar YouTube search (unchanged)
    if yt_query:
        debug_print(f"Processing sidebar search: '{yt_query}'")
        try:
            # Translate sidebar query if needed
            english_yt_query = yt_query
            if language_code != "en":
                try:
                    debug_print("Translating sidebar query")
                    english_yt_query, _ = translate_query_to_english(yt_query, language_code)
                    debug_print(f"Translated sidebar query: '{english_yt_query}'")
                except Exception as e:
                    debug_print(f"Translation error in sidebar: {e}", "error")
                    debug_print(f"Trace: {traceback.format_exc()}", "error")
                    english_yt_query = yt_query
                    debug_print("Using original sidebar query due to translation error")
                
            debug_print("Finding sidebar videos")
            sidebar_results = safe_get_videos(english_yt_query)
            debug_print(f"Found {len(sidebar_results)} sidebar videos")
            
            sidebar_results_text = {
                "en": "🔍 Video Results:",
                "hi": "🔍 वीडियो परिणाम:",
                "mr": "🔍 व्हिडिओ परिणाम:"
            }.get(language_code, "🔍 Video Results:")
            
            no_sidebar_results_text = {
                "en": "No videos found. Try using different keywords.",
                "hi": "कोई वीडियो नहीं मिला। अलग कीवर्ड का उपयोग करके देखें।",
                "mr": "कोणतेही व्हिडिओ सापडले नाहीत. वेगळे कीवर्ड वापरून पहा."
            }.get(language_code, "No videos found. Try using different keywords.")
            
            if sidebar_results:
                st.sidebar.markdown(f"### {sidebar_results_text}")
                for video in sidebar_results:
                    st.sidebar.markdown(f"**{video['title']}**  \n[Watch Video]({video['url']})")
            else:
                st.sidebar.info(no_sidebar_results_text)
        except Exception as e:
            debug_print(f"Error in sidebar search: {e}", "error")
            debug_print(f"Trace: {traceback.format_exc()}", "error")
            st.sidebar.error(f"Error in sidebar search: {str(e)}")
            
    # Display debug logs if debug mode is on
    if st.session_state.debug_mode:
        with st.expander("Debug Logs", expanded=False):
            st.write("Debug mode is enabled. Detailed logs are being captured.")
            st.write("Check the terminal/console for complete logs.")
            st.write(f"Current call step: {st.session_state.get('call_step', 'None')}")
            st.write(f"Call status: {st.session_state.get('call_status', 'None')}")
            st.write(f"Phone number: {st.session_state.get('phone_number', 'None')}")
            st.write(f"Current query: {st.session_state.get('current_query', 'None')}")
            st.write(f"Greeting played step 1: {st.session_state.get('greeting_played_step_1', 'None')}")
            st.write(f"Greeting played step 2: {st.session_state.get('greeting_played_step_2', 'None')}")
            st.write(f"Greeting played step 3: {st.session_state.get('greeting_played_step_3', 'None')}")
            if st.session_state.get('video_links', []):
                st.write(f"Number of video links: {len(st.session_state.video_links)}")

# Run the app
if __name__ == "__main__":
    debug_print("Starting Enertech Voice Support Assistant")
    try:
        main()
    except Exception as e:
        debug_print(f"Critical application error: {e}", "error")
        debug_print(f"Trace: {traceback.format_exc()}", "error")
        st.error(f"Application Error: {str(e)}")
        st.error("Please refresh the page and try again.")
    debug_print("Application execution completed")