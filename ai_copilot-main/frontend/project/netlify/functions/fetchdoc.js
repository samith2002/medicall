const { createClient } = require('@supabase/supabase-js');

// Environment variable validation
const requiredEnvVars = {
  SUPABASE_URL: process.env.SUPABASE_URL,
  SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY,
};

const missingVars = Object.entries(requiredEnvVars)
  .filter(([_, value]) => !value)
  .map(([key]) => key);

if (missingVars.length > 0) {
  throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
}

// Initialize Supabase client
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

// Fetch all doctors
const fetchAllDoctors = async () => {
  console.log('[DEBUG] Fetching all doctors');
  try {
    const { data: doctors, error } = await supabase
      .from('doctor')
      .select('doctorname, specialization'); // Fetch only doctorname and specialization

    if (error) {
      console.error('[ERROR] Failed to fetch doctors:', error.message);
      throw new Error(`Failed to fetch doctors: ${error.message}`);
    }

    if (!doctors || doctors.length === 0) {
      console.log('[DEBUG] No doctors found in the database');
      return {
        doctors: [],
        message: 'No doctors are available in the system.'
      };
    }

    const doctorList = doctors.map(doctor => ({
      name: doctor.doctorname,
      specialization: doctor.specialization,
    }));

    console.log('[DEBUG] All doctors retrieved:', doctorList);
    return {
      doctors: doctorList,
      message: `${doctorList.length} doctor(s) found in the system.`,
    };
  } catch (error) {
    console.error('[ERROR] Fetch all doctors failed:', error.message);
    throw error;
  }
};

exports.handler = async (event) => {
  console.log('[DEBUG] Fetch all doctors webhook received');

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const payload = JSON.parse(event.body || '');
    console.log('[DEBUG] Payload:', payload);

    if (payload.type !== 'function-call' || !payload.functionCall) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Invalid request type, expected function-call' }),
      };
    }

    const { name, parameters, toolCallId } = payload.functionCall;
    console.log('[DEBUG] Function call:', { name, parameters, toolCallId });

    if (name !== 'fetchAllDoctors') {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: `Invalid function name: ${name}, expected fetchAllDoctors` }),
      };
    }

    const result = await fetchAllDoctors();

    return {
      statusCode: 200,
      body: JSON.stringify({
        toolCallId,
        result,
      }),
    };
  } catch (error) {
    console.error('[ERROR] Processing fetch all doctors webhook:', error.message, error.stack);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        details: error.message,
      }),
    };
  }
};