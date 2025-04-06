// Environment variable validation
const requiredEnvVars = {
  SUPABASE_URL: process.env.SUPABASE_URL,
  SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY,
  GEMINI_API_KEY: process.env.GEMINI_API_KEY,
};

const missingVars = Object.entries(requiredEnvVars)
  .filter(([_, value]) => !value)
  .map(([key]) => key);

if (missingVars.length > 0) {
  throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
}

const { createClient } = require('@supabase/supabase-js');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Initialize Supabase client
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

// Initialize Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const extractStructuredData = async (payload) => {
  console.log('[DEBUG] Starting structured data extraction');
  const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });
  const prompt = `Extract ONLY the following key information from this appointment conversation summary and transcript. Return a JSON object with these fields:
  {
    "doctor": {
      "name": string (extract full name including Dr. title if present)
    },
    "patient": {
      "name": string (extract full name),
      "age": number (extract age if mentioned, null if not),
      "phoneNumber": string (extract phone number if mentioned, digits only, null if not)
    },
    "appointment": {
      "date": string (YYYY-MM-DD format, null if not scheduled),
      "startTime": string (HH:MM format in 24-hour time, null if not scheduled),
      "endTime": string (HH:MM format, 30 minutes after startTime, null if not scheduled)
    }
  }

  Summary: ${payload.message.analysis.summary}
  
  Transcript excerpts:
  ${payload.message.transcript}
  
  Rules:
  - Convert all times to 24-hour format
  - Format phone numbers as strings with just digits (no spaces or special characters)
  - Use the current year (${new Date().getFullYear()}) if year is not specified in the date
  - Ensure appointment endTime is exactly 30 minutes after startTime
  - If no appointment was scheduled, set appointment fields to null
  - Return ONLY the JSON object, no markdown or code block syntax`;

  try {
    const result = await model.generateContent(prompt);
    const response = await result.response;
    let text = response.text();
    console.log('[DEBUG] Raw structured data:', text);

    text = text.replace(/^```json\s*/, '').replace(/\s*```$/, '');
    if (!text.trim().startsWith('{')) {
      throw new Error('Response is not a JSON object');
    }

    const structuredData = JSON.parse(text);
    console.log('[DEBUG] Parsed structured data:', structuredData);
    return structuredData;
  } catch (error) {
    console.error('[ERROR] Structured data extraction failed:', error.message, error.stack);
    throw error;
  }
};

const insertPatientData = async (patientData) => {
  console.log('[DEBUG] Processing patient data:', patientData);

  if (!patientData.name) {
    throw new Error('Patient name is required');
  }

  try {
    // Fetch existing patient (lowercase table name)
    const { data: patient, error: fetchError } = await supabase
      .from('patient') // Changed to lowercase
      .select('patientid') // Adjusted to lowercase column name
      .eq('patientname', patientData.name) // Adjusted to lowercase column name
      .maybeSingle();

    if (fetchError) {
      console.error('[ERROR] Failed to fetch patient:', fetchError.message, fetchError);
      throw fetchError;
    }

    if (!patient) {
      console.log('[DEBUG] No existing patient found, creating new one');
      const { data: newPatient, error: insertError } = await supabase
        .from('patient') // Changed to lowercase
        .insert({
          patientname: patientData.name, // Adjusted to lowercase column name
          age: patientData.age || null, // Adjusted to lowercase column name
          phonenumber: patientData.phoneNumber || null, // Adjusted to lowercase column name
        })
        .select('patientid') // Adjusted to lowercase column name
        .single();

      if (insertError) {
        console.error('[ERROR] Failed to insert patient:', insertError.message, insertError);
        throw insertError;
      }

      console.log('[DEBUG] New patient created:', newPatient);
      return newPatient.patientid; // Adjusted to lowercase
    }

    // Update existing patient if new data is provided
    if (patientData.age || patientData.phoneNumber) {
      const updateData = {};
      if (patientData.age) updateData.age = patientData.age; // Adjusted to lowercase
      if (patientData.phoneNumber) updateData.phonenumber = patientData.phoneNumber; // Adjusted to lowercase
      updateData.updatedat = new Date().toISOString(); // Adjusted to lowercase

      const { error: updateError } = await supabase
        .from('patient') // Changed to lowercase
        .update(updateData)
        .eq('patientid', patient.patientid); // Adjusted to lowercase

      if (updateError) {
        console.error('[ERROR] Failed to update patient:', updateError.message, updateError);
        throw updateError;
      }
    }

    console.log('[DEBUG] Existing patient ID:', patient.patientid);
    return patient.patientid; // Adjusted to lowercase
  } catch (error) {
    console.error('[ERROR] Patient processing failed:', error.message, error);
    throw error;
  }
};

const getDoctorID = async (doctorName) => {
  console.log('[DEBUG] Fetching doctor ID for:', doctorName);
  try {
    const { data: doctor, error } = await supabase
      .from('doctor') // Changed to lowercase
      .select('doctorid') // Adjusted to lowercase column name
      .eq('doctorname', doctorName) // Adjusted to lowercase column name
      .single();

    if (error || !doctor) {
      console.error('[ERROR] Doctor not found:', doctorName, error?.message);
      throw new Error(`Doctor not found: ${doctorName}`);
    }

    console.log('[DEBUG] Found doctor:', doctor);
    return doctor.doctorid; // Adjusted to lowercase
  } catch (error) {
    console.error('[ERROR] Doctor lookup failed:', error.message, error);
    throw error;
  }
};

const createAppointment = async (doctorId, patientId, appointmentData) => {
  console.log('[DEBUG] Creating appointment:', { doctorId, patientId, appointmentData });

  if (!appointmentData.date || !appointmentData.startTime || !appointmentData.endTime) {
    console.log('[DEBUG] No appointment data provided, skipping creation');
    return null;
  }

  try {
    const { data: appointment, error } = await supabase
      .from('appointments') // Changed to lowercase
      .insert({
        doctorid: doctorId, // Adjusted to lowercase column name
        patientid: patientId, // Adjusted to lowercase column name
        date: appointmentData.date, // Adjusted to lowercase column name
        starttime: appointmentData.startTime, // Adjusted to lowercase column name
        endtime: appointmentData.endTime, // Adjusted to lowercase column name
      })
      .select()
      .single();

    if (error) {
      console.error('[ERROR] Failed to create appointment:', error.message, error);
      throw error;
    }

    console.log('[DEBUG] Appointment created:', appointment);
    return appointment;
  } catch (error) {
    console.error('[ERROR] Appointment creation failed:', error.message, error);
    throw error;
  }
};

exports.handler = async (event) => {
  console.log('[DEBUG] Webhook received');

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    if (!supabase) {
      throw new Error('Supabase client not initialized');
    }

    // Debug: Test Supabase connection
    const { data: testData, error: testError } = await supabase.from('patient').select('*').limit(1);
    console.log('[DEBUG] Supabase connection test:', testData, testError);

    const payload = JSON.parse(event.body || '');
    console.log('[DEBUG] Webhook payload type:', payload.message.type);

    if (payload.message.type !== 'end-of-call-report') {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Invalid webhook type' }),
      };
    }

    // Step 1: Extract structured data
    const structuredData = await extractStructuredData(payload);
    console.log('[DEBUG] Structured data extracted:', structuredData);

    // Step 2: Process patient
    const patientId = await insertPatientData(structuredData.patient);

    // Step 3: Get doctor ID
    const doctorId = await getDoctorID(structuredData.doctor.name);

    // Step 4: Create appointment (if scheduled)
    const appointment = await createAppointment(doctorId, patientId, structuredData.appointment);

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: appointment ? 'Appointment created successfully' : 'No appointment scheduled',
        data: {
          appointment,
          patientId,
          doctorId,
          recordingUrl: payload.message.recording_url,
          callDuration: payload.message.duration_seconds,
          endReason: payload.message.ended_reason,
        },
      }),
    };
  } catch (error) {
    console.error('[ERROR] Processing webhook:', error.message, error.stack);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        details: error.message,
      }),
    };
  }
};