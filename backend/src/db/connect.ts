// Shared MongoDB Atlas connection via Mongoose. Each flow defines its own
// models in its own flow file.
// Owner: member1

// TODO(member1): mongoose.connect(process.env.MONGODB_URI), fail with a clear
// message when the variable is missing, log connection errors.
export async function connectDb(): Promise<void> {
  throw new Error("TODO(member1): connectDb not implemented");
}
