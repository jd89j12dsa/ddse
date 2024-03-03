/**
 * Autogenerated by Thrift Compiler (0.13.0)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
#include "SSEService.h"

namespace server {


SSEService_add_entries_args::~SSEService_add_entries_args() noexcept {
}


uint32_t SSEService_add_entries_args::read(::apache::thrift::protocol::TProtocol* iprot) {

  ::apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->label);
          this->__isset.label = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 2:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->tag);
          this->__isset.tag = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 3:
        if (ftype == ::apache::thrift::protocol::T_LIST) {
          {
            this->ciphertext_list.clear();
            uint32_t _size2;
            ::apache::thrift::protocol::TType _etype5;
            xfer += iprot->readListBegin(_etype5, _size2);
            this->ciphertext_list.resize(_size2);
            uint32_t _i6;
            for (_i6 = 0; _i6 < _size2; ++_i6)
            {
              xfer += iprot->readString(this->ciphertext_list[_i6]);
            }
            xfer += iprot->readListEnd();
          }
          this->__isset.ciphertext_list = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t SSEService_add_entries_args::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  ::apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("SSEService_add_entries_args");

  xfer += oprot->writeFieldBegin("label", ::apache::thrift::protocol::T_STRING, 1);
  xfer += oprot->writeString(this->label);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("tag", ::apache::thrift::protocol::T_STRING, 2);
  xfer += oprot->writeString(this->tag);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("ciphertext_list", ::apache::thrift::protocol::T_LIST, 3);
  {
    xfer += oprot->writeListBegin(::apache::thrift::protocol::T_STRING, static_cast<uint32_t>(this->ciphertext_list.size()));
    std::vector<std::string> ::const_iterator _iter7;
    for (_iter7 = this->ciphertext_list.begin(); _iter7 != this->ciphertext_list.end(); ++_iter7)
    {
      xfer += oprot->writeString((*_iter7));
    }
    xfer += oprot->writeListEnd();
  }
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


SSEService_add_entries_pargs::~SSEService_add_entries_pargs() noexcept {
}


uint32_t SSEService_add_entries_pargs::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  ::apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("SSEService_add_entries_pargs");

  xfer += oprot->writeFieldBegin("label", ::apache::thrift::protocol::T_STRING, 1);
  xfer += oprot->writeString((*(this->label)));
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("tag", ::apache::thrift::protocol::T_STRING, 2);
  xfer += oprot->writeString((*(this->tag)));
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("ciphertext_list", ::apache::thrift::protocol::T_LIST, 3);
  {
    xfer += oprot->writeListBegin(::apache::thrift::protocol::T_STRING, static_cast<uint32_t>((*(this->ciphertext_list)).size()));
    std::vector<std::string> ::const_iterator _iter8;
    for (_iter8 = (*(this->ciphertext_list)).begin(); _iter8 != (*(this->ciphertext_list)).end(); ++_iter8)
    {
      xfer += oprot->writeString((*_iter8));
    }
    xfer += oprot->writeListEnd();
  }
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


SSEService_search_args::~SSEService_search_args() noexcept {
}


uint32_t SSEService_search_args::read(::apache::thrift::protocol::TProtocol* iprot) {

  ::apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->token);
          this->__isset.token = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 2:
        if (ftype == ::apache::thrift::protocol::T_LIST) {
          {
            this->node_list.clear();
            uint32_t _size9;
            ::apache::thrift::protocol::TType _etype12;
            xfer += iprot->readListBegin(_etype12, _size9);
            this->node_list.resize(_size9);
            uint32_t _i13;
            for (_i13 = 0; _i13 < _size9; ++_i13)
            {
              xfer += this->node_list[_i13].read(iprot);
            }
            xfer += iprot->readListEnd();
          }
          this->__isset.node_list = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 3:
        if (ftype == ::apache::thrift::protocol::T_I32) {
          xfer += iprot->readI32(this->level);
          this->__isset.level = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t SSEService_search_args::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  ::apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("SSEService_search_args");

  xfer += oprot->writeFieldBegin("token", ::apache::thrift::protocol::T_STRING, 1);
  xfer += oprot->writeString(this->token);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("node_list", ::apache::thrift::protocol::T_LIST, 2);
  {
    xfer += oprot->writeListBegin(::apache::thrift::protocol::T_STRUCT, static_cast<uint32_t>(this->node_list.size()));
    std::vector<SerialisedNode> ::const_iterator _iter14;
    for (_iter14 = this->node_list.begin(); _iter14 != this->node_list.end(); ++_iter14)
    {
      xfer += (*_iter14).write(oprot);
    }
    xfer += oprot->writeListEnd();
  }
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("level", ::apache::thrift::protocol::T_I32, 3);
  xfer += oprot->writeI32(this->level);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


SSEService_search_pargs::~SSEService_search_pargs() noexcept {
}


uint32_t SSEService_search_pargs::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  ::apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("SSEService_search_pargs");

  xfer += oprot->writeFieldBegin("token", ::apache::thrift::protocol::T_STRING, 1);
  xfer += oprot->writeString((*(this->token)));
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("node_list", ::apache::thrift::protocol::T_LIST, 2);
  {
    xfer += oprot->writeListBegin(::apache::thrift::protocol::T_STRUCT, static_cast<uint32_t>((*(this->node_list)).size()));
    std::vector<SerialisedNode> ::const_iterator _iter15;
    for (_iter15 = (*(this->node_list)).begin(); _iter15 != (*(this->node_list)).end(); ++_iter15)
    {
      xfer += (*_iter15).write(oprot);
    }
    xfer += oprot->writeListEnd();
  }
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("level", ::apache::thrift::protocol::T_I32, 3);
  xfer += oprot->writeI32((*(this->level)));
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


SSEService_search_result::~SSEService_search_result() noexcept {
}


uint32_t SSEService_search_result::read(::apache::thrift::protocol::TProtocol* iprot) {

  ::apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 0:
        if (ftype == ::apache::thrift::protocol::T_LIST) {
          {
            this->success.clear();
            uint32_t _size16;
            ::apache::thrift::protocol::TType _etype19;
            xfer += iprot->readListBegin(_etype19, _size16);
            this->success.resize(_size16);
            uint32_t _i20;
            for (_i20 = 0; _i20 < _size16; ++_i20)
            {
              xfer += iprot->readI32(this->success[_i20]);
            }
            xfer += iprot->readListEnd();
          }
          this->__isset.success = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t SSEService_search_result::write(::apache::thrift::protocol::TProtocol* oprot) const {

  uint32_t xfer = 0;

  xfer += oprot->writeStructBegin("SSEService_search_result");

  if (this->__isset.success) {
    xfer += oprot->writeFieldBegin("success", ::apache::thrift::protocol::T_LIST, 0);
    {
      xfer += oprot->writeListBegin(::apache::thrift::protocol::T_I32, static_cast<uint32_t>(this->success.size()));
      std::vector<int32_t> ::const_iterator _iter21;
      for (_iter21 = this->success.begin(); _iter21 != this->success.end(); ++_iter21)
      {
        xfer += oprot->writeI32((*_iter21));
      }
      xfer += oprot->writeListEnd();
    }
    xfer += oprot->writeFieldEnd();
  }
  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}


SSEService_search_presult::~SSEService_search_presult() noexcept {
}


uint32_t SSEService_search_presult::read(::apache::thrift::protocol::TProtocol* iprot) {

  ::apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 0:
        if (ftype == ::apache::thrift::protocol::T_LIST) {
          {
            (*(this->success)).clear();
            uint32_t _size22;
            ::apache::thrift::protocol::TType _etype25;
            xfer += iprot->readListBegin(_etype25, _size22);
            (*(this->success)).resize(_size22);
            uint32_t _i26;
            for (_i26 = 0; _i26 < _size22; ++_i26)
            {
              xfer += iprot->readI32((*(this->success))[_i26]);
            }
            xfer += iprot->readListEnd();
          }
          this->__isset.success = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

void SSEServiceClient::add_entries(const std::string& label, const std::string& tag, const std::vector<std::string> & ciphertext_list)
{
  send_add_entries(label, tag, ciphertext_list);
}

void SSEServiceClient::send_add_entries(const std::string& label, const std::string& tag, const std::vector<std::string> & ciphertext_list)
{
  int32_t cseqid = 0;
  oprot_->writeMessageBegin("add_entries", ::apache::thrift::protocol::T_ONEWAY, cseqid);

  SSEService_add_entries_pargs args;
  args.label = &label;
  args.tag = &tag;
  args.ciphertext_list = &ciphertext_list;
  args.write(oprot_);

  oprot_->writeMessageEnd();
  oprot_->getTransport()->writeEnd();
  oprot_->getTransport()->flush();
}

void SSEServiceClient::search(std::vector<int32_t> & _return, const std::string& token, const std::vector<SerialisedNode> & node_list, const int32_t level)
{
  send_search(token, node_list, level);
  recv_search(_return);
}

void SSEServiceClient::send_search(const std::string& token, const std::vector<SerialisedNode> & node_list, const int32_t level)
{
  int32_t cseqid = 0;
  oprot_->writeMessageBegin("search", ::apache::thrift::protocol::T_CALL, cseqid);

  SSEService_search_pargs args;
  args.token = &token;
  args.node_list = &node_list;
  args.level = &level;
  args.write(oprot_);

  oprot_->writeMessageEnd();
  oprot_->getTransport()->writeEnd();
  oprot_->getTransport()->flush();
}

void SSEServiceClient::recv_search(std::vector<int32_t> & _return)
{

  int32_t rseqid = 0;
  std::string fname;
  ::apache::thrift::protocol::TMessageType mtype;

  iprot_->readMessageBegin(fname, mtype, rseqid);
  if (mtype == ::apache::thrift::protocol::T_EXCEPTION) {
    ::apache::thrift::TApplicationException x;
    x.read(iprot_);
    iprot_->readMessageEnd();
    iprot_->getTransport()->readEnd();
    throw x;
  }
  if (mtype != ::apache::thrift::protocol::T_REPLY) {
    iprot_->skip(::apache::thrift::protocol::T_STRUCT);
    iprot_->readMessageEnd();
    iprot_->getTransport()->readEnd();
  }
  if (fname.compare("search") != 0) {
    iprot_->skip(::apache::thrift::protocol::T_STRUCT);
    iprot_->readMessageEnd();
    iprot_->getTransport()->readEnd();
  }
  SSEService_search_presult result;
  result.success = &_return;
  result.read(iprot_);
  iprot_->readMessageEnd();
  iprot_->getTransport()->readEnd();

  if (result.__isset.success) {
    // _return pointer has now been filled
    return;
  }
  throw ::apache::thrift::TApplicationException(::apache::thrift::TApplicationException::MISSING_RESULT, "search failed: unknown result");
}

bool SSEServiceProcessor::dispatchCall(::apache::thrift::protocol::TProtocol* iprot, ::apache::thrift::protocol::TProtocol* oprot, const std::string& fname, int32_t seqid, void* callContext) {
  ProcessMap::iterator pfn;
  pfn = processMap_.find(fname);
  if (pfn == processMap_.end()) {
    iprot->skip(::apache::thrift::protocol::T_STRUCT);
    iprot->readMessageEnd();
    iprot->getTransport()->readEnd();
    ::apache::thrift::TApplicationException x(::apache::thrift::TApplicationException::UNKNOWN_METHOD, "Invalid method name: '"+fname+"'");
    oprot->writeMessageBegin(fname, ::apache::thrift::protocol::T_EXCEPTION, seqid);
    x.write(oprot);
    oprot->writeMessageEnd();
    oprot->getTransport()->writeEnd();
    oprot->getTransport()->flush();
    return true;
  }
  (this->*(pfn->second))(seqid, iprot, oprot, callContext);
  return true;
}

void SSEServiceProcessor::process_add_entries(int32_t, ::apache::thrift::protocol::TProtocol* iprot, ::apache::thrift::protocol::TProtocol*, void* callContext)
{
  void* ctx = NULL;
  if (this->eventHandler_.get() != NULL) {
    ctx = this->eventHandler_->getContext("SSEService.add_entries", callContext);
  }
  ::apache::thrift::TProcessorContextFreer freer(this->eventHandler_.get(), ctx, "SSEService.add_entries");

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->preRead(ctx, "SSEService.add_entries");
  }

  SSEService_add_entries_args args;
  args.read(iprot);
  iprot->readMessageEnd();
  uint32_t bytes = iprot->getTransport()->readEnd();

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->postRead(ctx, "SSEService.add_entries", bytes);
  }

  try {
    iface_->add_entries(args.label, args.tag, args.ciphertext_list);
  } catch (const std::exception&) {
    if (this->eventHandler_.get() != NULL) {
      this->eventHandler_->handlerError(ctx, "SSEService.add_entries");
    }
    return;
  }

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->asyncComplete(ctx, "SSEService.add_entries");
  }

  return;
}

void SSEServiceProcessor::process_search(int32_t seqid, ::apache::thrift::protocol::TProtocol* iprot, ::apache::thrift::protocol::TProtocol* oprot, void* callContext)
{
  void* ctx = NULL;
  if (this->eventHandler_.get() != NULL) {
    ctx = this->eventHandler_->getContext("SSEService.search", callContext);
  }
  ::apache::thrift::TProcessorContextFreer freer(this->eventHandler_.get(), ctx, "SSEService.search");

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->preRead(ctx, "SSEService.search");
  }

  SSEService_search_args args;
  args.read(iprot);
  iprot->readMessageEnd();
  uint32_t bytes = iprot->getTransport()->readEnd();

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->postRead(ctx, "SSEService.search", bytes);
  }

  SSEService_search_result result;
  try {
    iface_->search(result.success, args.token, args.node_list, args.level);
    result.__isset.success = true;
  } catch (const std::exception& e) {
    if (this->eventHandler_.get() != NULL) {
      this->eventHandler_->handlerError(ctx, "SSEService.search");
    }

    ::apache::thrift::TApplicationException x(e.what());
    oprot->writeMessageBegin("search", ::apache::thrift::protocol::T_EXCEPTION, seqid);
    x.write(oprot);
    oprot->writeMessageEnd();
    oprot->getTransport()->writeEnd();
    oprot->getTransport()->flush();
    return;
  }

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->preWrite(ctx, "SSEService.search");
  }

  oprot->writeMessageBegin("search", ::apache::thrift::protocol::T_REPLY, seqid);
  result.write(oprot);
  oprot->writeMessageEnd();
  bytes = oprot->getTransport()->writeEnd();
  oprot->getTransport()->flush();

  if (this->eventHandler_.get() != NULL) {
    this->eventHandler_->postWrite(ctx, "SSEService.search", bytes);
  }
}

::std::shared_ptr< ::apache::thrift::TProcessor > SSEServiceProcessorFactory::getProcessor(const ::apache::thrift::TConnectionInfo& connInfo) {
  ::apache::thrift::ReleaseHandler< SSEServiceIfFactory > cleanup(handlerFactory_);
  ::std::shared_ptr< SSEServiceIf > handler(handlerFactory_->getHandler(connInfo), cleanup);
  ::std::shared_ptr< ::apache::thrift::TProcessor > processor(new SSEServiceProcessor(handler));
  return processor;
}

void SSEServiceConcurrentClient::add_entries(const std::string& label, const std::string& tag, const std::vector<std::string> & ciphertext_list)
{
  send_add_entries(label, tag, ciphertext_list);
}

void SSEServiceConcurrentClient::send_add_entries(const std::string& label, const std::string& tag, const std::vector<std::string> & ciphertext_list)
{
  int32_t cseqid = 0;
  ::apache::thrift::async::TConcurrentSendSentry sentry(this->sync_.get());
  oprot_->writeMessageBegin("add_entries", ::apache::thrift::protocol::T_ONEWAY, cseqid);

  SSEService_add_entries_pargs args;
  args.label = &label;
  args.tag = &tag;
  args.ciphertext_list = &ciphertext_list;
  args.write(oprot_);

  oprot_->writeMessageEnd();
  oprot_->getTransport()->writeEnd();
  oprot_->getTransport()->flush();

  sentry.commit();
}

void SSEServiceConcurrentClient::search(std::vector<int32_t> & _return, const std::string& token, const std::vector<SerialisedNode> & node_list, const int32_t level)
{
  int32_t seqid = send_search(token, node_list, level);
  recv_search(_return, seqid);
}

int32_t SSEServiceConcurrentClient::send_search(const std::string& token, const std::vector<SerialisedNode> & node_list, const int32_t level)
{
  int32_t cseqid = this->sync_->generateSeqId();
  ::apache::thrift::async::TConcurrentSendSentry sentry(this->sync_.get());
  oprot_->writeMessageBegin("search", ::apache::thrift::protocol::T_CALL, cseqid);

  SSEService_search_pargs args;
  args.token = &token;
  args.node_list = &node_list;
  args.level = &level;
  args.write(oprot_);

  oprot_->writeMessageEnd();
  oprot_->getTransport()->writeEnd();
  oprot_->getTransport()->flush();

  sentry.commit();
  return cseqid;
}

void SSEServiceConcurrentClient::recv_search(std::vector<int32_t> & _return, const int32_t seqid)
{

  int32_t rseqid = 0;
  std::string fname;
  ::apache::thrift::protocol::TMessageType mtype;

  // the read mutex gets dropped and reacquired as part of waitForWork()
  // The destructor of this sentry wakes up other clients
  ::apache::thrift::async::TConcurrentRecvSentry sentry(this->sync_.get(), seqid);

  while(true) {
    if(!this->sync_->getPending(fname, mtype, rseqid)) {
      iprot_->readMessageBegin(fname, mtype, rseqid);
    }
    if(seqid == rseqid) {
      if (mtype == ::apache::thrift::protocol::T_EXCEPTION) {
        ::apache::thrift::TApplicationException x;
        x.read(iprot_);
        iprot_->readMessageEnd();
        iprot_->getTransport()->readEnd();
        sentry.commit();
        throw x;
      }
      if (mtype != ::apache::thrift::protocol::T_REPLY) {
        iprot_->skip(::apache::thrift::protocol::T_STRUCT);
        iprot_->readMessageEnd();
        iprot_->getTransport()->readEnd();
      }
      if (fname.compare("search") != 0) {
        iprot_->skip(::apache::thrift::protocol::T_STRUCT);
        iprot_->readMessageEnd();
        iprot_->getTransport()->readEnd();

        // in a bad state, don't commit
        using ::apache::thrift::protocol::TProtocolException;
        throw TProtocolException(TProtocolException::INVALID_DATA);
      }
      SSEService_search_presult result;
      result.success = &_return;
      result.read(iprot_);
      iprot_->readMessageEnd();
      iprot_->getTransport()->readEnd();

      if (result.__isset.success) {
        // _return pointer has now been filled
        sentry.commit();
        return;
      }
      // in a bad state, don't commit
      throw ::apache::thrift::TApplicationException(::apache::thrift::TApplicationException::MISSING_RESULT, "search failed: unknown result");
    }
    // seqid != rseqid
    this->sync_->updatePending(fname, mtype, rseqid);

    // this will temporarily unlock the readMutex, and let other clients get work done
    this->sync_->waitForWork(seqid);
  } // end while(true)
}

} // namespace

